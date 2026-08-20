"""Service-layer test — exercise book business logic against the test DB."""

from app.schemas.book import BookForm
from app.services import books as book_service


async def test_create_and_fetch_book(db_session):
    form = BookForm(
        title="کتاب تست",
        authors=["نویسندهٔ تست"],
        slug="test-book",
        status="published",
        show_in_library=True,
    )

    book = await book_service.create_book(db_session, form)
    assert book.id is not None
    assert book.slug == "test-book"

    fetched = await book_service.get_book_by_slug(db_session, "test-book")
    assert fetched is not None
    assert fetched.title == "کتاب تست"

    library_books = await book_service.list_books(
        db_session, published_only=True, library_only=True
    )
    assert any(b.slug == "test-book" for b in library_books)
