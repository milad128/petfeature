# Product Spec v7 — پت فیچر (Admin Reply to Post Comments)

> **Prerequisite:** [Product Spec v6](./product-spec-v6.md) must be shipped · **Parent:** [Product overview](./product-spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v7 — Admin Reply to Post Comments |
| **Status** | Shipped |
| **Goal** | Allow Milad to write a reply to visitor comments on blog posts, displayed publicly beneath the original comment |
| **Scope** | Blog posts only (`PostComment`) — book comments excluded |

**Scope in one sentence:** Add a nullable `reply` field to `PostComment`; surface a reply textarea in the admin comment moderation page; display the reply publicly on the post detail page beneath the approved comment.

---

## 2. Problem & Goals

**Problem:** Visitors leave comments on blog posts and receive no response. There is currently no mechanism for Milad to reply publicly — he can only approve, reject, or delete. This makes the blog feel one-directional and reduces the value of the comment section for visitors who ask questions or share feedback.

**v7 goals:**

- Milad can write a reply to any approved comment from the admin panel
- The reply appears publicly on the post page, visually distinct from the original comment and clearly attributed to Milad ("میلاد")
- Replies are optional — unanswered comments display as they do today
- Implementation is minimal: one new DB column, one new admin action, one template update

---

## 3. Scope Decision: Posts Only

Book comments (`BookComment`) are **excluded** from v7. Reasons:
- Book comment volume is expected to be lower
- The book detail page already has a denser layout
- Keeping v7 scoped to one model reduces implementation risk

Book comment replies can be added in a future version using the same pattern.

---

## 4. Data Model Changes

### 4.1 `PostComment` — two new columns

```python
reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
# Admin's reply text. None means no reply has been written.

reply_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
)
# Timestamp set automatically when reply is first saved.
```

No new model, no new table. Single Alembic migration adds both columns with `nullable=True` and no default (existing rows get `NULL` — i.e., no reply).

### 4.2 Migration

One Alembic revision:
- `ALTER TABLE post_comments ADD COLUMN reply TEXT`
- `ALTER TABLE post_comments ADD COLUMN reply_at TIMESTAMP WITH TIME ZONE`

No data backfill needed.

---

## 5. Admin CMS Changes

### 5.1 Where the reply UI lives

The reply field is added to the **existing comment moderation page** at `/admin/posts/comments/`. It appears **only on approved comments** — there is no point replying to a pending or rejected comment.

### 5.2 Reply UI per comment row

For each **approved** comment, below the comment text, add:

```
[ existing comment card: author name, date, body, action buttons ]

  ─────────────────────────────────────────────────
  پاسخ شما (optional)
  ┌──────────────────────────────────────────────┐
  │  textarea, placeholder: "پاسخ بنویسید…"     │
  └──────────────────────────────────────────────┘
  [ ذخیره پاسخ ]    (if reply exists: small muted label "پاسخ داده شده — تاریخ")
```

- If `reply` is `NULL`: textarea is empty, button label is "ذخیره پاسخ"
- If `reply` exists: textarea is pre-filled with the existing reply text, button label is "ویرایش پاسخ", and a muted timestamp label shows when it was first saved
- Saving an empty reply clears/removes the existing reply (sets both fields to `NULL`)

### 5.3 Reply action route

| Method | Path | Handler |
|--------|------|---------|
| POST | `/admin/posts/comments/{comment_id}/reply/` | `admin/routes.py` |

**Behavior:**
- Guard: admin must be authenticated
- Load `PostComment` by `comment_id`; 404 silently redirects to `/admin/posts/comments/` if not found
- If `reply` field in POST body is non-empty (stripped):
  - Save `reply` text to `PostComment.reply`
  - If `PostComment.reply_at` is `None`, set `reply_at = now()` (only set on first save — preserve original timestamp on edits)
- If `reply` is empty:
  - Set `PostComment.reply = None`, `PostComment.reply_at = None`
- Redirect to `/admin/posts/comments/?status=approved` after save

### 5.4 No separate reply page

Reply is edited inline on the moderation list page — no dedicated form page needed. The textarea in the list is sufficient given the short nature of replies.

---

## 6. Public Display — Post Detail Page

### 6.1 Template change

In `app/templates/pages/post_detail.html`, inside the `{% for c in post.approved_comments %}` loop, add a reply block below the comment body:

```
┌─────────────────────────────────────────────────┐
│  [Author name]                    [Jalali date]  │
│  [Comment body text]                             │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ 🗨 میلاد                    [reply date]  │  │  ← reply block
│  │ [reply text]                              │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Visual design intent:**
- Reply block is visually inset or indented relative to the original comment
- Reply author label: "میلاد" (hardcoded — single admin site, no need for a configurable author name here)
- Reply date: Jalali format of `reply_at`
- Reply block should use a slightly different background or left-border accent to distinguish it from the original comment
- If `c.reply` is `None` or empty: reply block is not rendered (no empty state shown to visitors)

### 6.2 No change to comment count

`post.approved_comment_count` and `post.approved_comments` are unchanged — replies are not counted as separate comments.

---

## 7. User Stories

- *As Milad (admin), I want to write a reply to a visitor's comment so that the conversation feels alive and visitors feel heard*
- *As Milad (admin), I want to edit my existing reply in case I want to correct or expand it*
- *As Milad (admin), I want to delete my reply (by clearing the textarea) if I no longer want it shown*
- *As a visitor, I want to see Milad's reply beneath my comment so I know my question was answered*
- *As a visitor reading the comments, I want replies to be visually distinct from original comments so I can follow the conversation easily*

---

## 8. Acceptance Criteria

### Admin
- [ ] Each approved comment on `/admin/posts/comments/?status=approved` shows a reply textarea below the comment body
- [ ] Submitting a non-empty reply saves it to `PostComment.reply` and sets `reply_at` (only on first save)
- [ ] Submitting an empty reply clears `PostComment.reply` and `PostComment.reply_at`
- [ ] After saving, the page redirects to `/admin/posts/comments/?status=approved` and the textarea reflects the saved reply
- [ ] Reply textarea is **not shown** on pending or rejected comment tabs
- [ ] Existing comments that have no reply show an empty textarea with placeholder text

### Public
- [ ] On the post detail page, approved comments with a non-null `reply` show the reply block beneath the comment body
- [ ] Reply block shows "میلاد" as the author label and the `reply_at` date in Jalali format
- [ ] Approved comments with `reply = NULL` show no reply block (no empty state, no placeholder)
- [ ] Existing comments without a reply render identically to today (no visual regression)

### Migration
- [ ] Alembic migration adds `reply` (TEXT, nullable) and `reply_at` (TIMESTAMPTZ, nullable) to `post_comments`
- [ ] All existing `PostComment` rows have `reply = NULL` and `reply_at = NULL` after migration

---

## 9. Out of Scope

| Feature | Reason |
|---------|--------|
| Book comment replies | Deferred — same pattern, different version |
| Visitor-to-visitor threaded replies | No auth; site is not a forum |
| Email notification to commenter when replied | No email service in scope |
| Reply visible on comment moderation list (pending/rejected tabs) | No value — replies are for approved comments only |
| Multiple replies per comment | One reply per comment is sufficient for a personal blog |
| Rich text in replies | Plain text is consistent with the rest of the site |
| Configurable reply author name | Hardcoded "میلاد" — single author site |

---

## 10. Technical Notes for Engineer

### Files to change

| File | Change |
|------|--------|
| `app/models/post.py` | Add `reply` and `reply_at` to `PostComment` |
| `app/services/posts.py` | Add `save_comment_reply(db, comment, reply_text)` function |
| `app/admin/routes.py` | Add `POST /admin/posts/comments/{id}/reply/` route |
| `app/templates/admin/post_comments_list.html` | Add reply textarea + save button to each approved comment row |
| `app/templates/pages/post_detail.html` | Add reply block inside approved comments loop |
| `alembic/versions/` | New migration: add `reply` + `reply_at` columns |

### Service function signature (suggested)

```python
async def save_comment_reply(
    db: AsyncSession,
    comment: PostComment,
    reply_text: str,  # already stripped; empty string means clear
) -> PostComment:
    if reply_text:
        comment.reply = reply_text
        if comment.reply_at is None:
            comment.reply_at = datetime.now(timezone.utc)
    else:
        comment.reply = None
        comment.reply_at = None
    await db.commit()
    await db.refresh(comment)
    return comment
```

### Template — reply block (post_detail.html, suggested)

```html
{% if c.reply %}
<div class="comment-reply">
  <div class="comment-reply-head">
    <span class="comment-reply-author">میلاد</span>
    <span class="comment-reply-date">{{ c.reply_at | jalali }}</span>
  </div>
  <p class="comment-reply-body">{{ c.reply }}</p>
</div>
{% endif %}
```

### Template — reply form (post_comments_list.html, suggested)

```html
{% if c.status == 'approved' %}
<form method="post" action="/admin/posts/comments/{{ c.id }}/reply/">
  <textarea name="reply" placeholder="پاسخ بنویسید…">{{ c.reply or '' }}</textarea>
  <button type="submit">
    {% if c.reply %}ویرایش پاسخ{% else %}ذخیره پاسخ{% endif %}
  </button>
  {% if c.reply_at %}
  <span class="reply-timestamp">پاسخ داده شده — {{ c.reply_at | jalali }}</span>
  {% endif %}
</form>
{% endif %}
```

---

## 11. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should the reply author label "میلاد" be pulled from `AboutPage.author_name` instead of hardcoded? | Milad | Nice-to-have; hardcode for v7, refactor later |
| Should saving a reply also auto-approve the comment if it was pending? | Milad | Assumed no — approval and reply are independent actions |
| Should the reply textarea appear on the `pending` tab (so Milad can pre-write a reply before approving)? | Milad | Assumed no for simplicity; approve first, then reply |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*Spec version: 1.0 · July 2026*
