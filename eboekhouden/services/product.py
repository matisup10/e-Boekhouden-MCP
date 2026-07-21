"""Product service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.product import (
    CreateProduct,
    CreatedProduct,
    PatchProduct,
    Product,
    ProductGroup,
    ProductGroupList,
    ProductList,
    ProductListItem,
)
from eboekhouden.services.base import BaseService


class ProductService(BaseService):
    """Service for product endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        code: str | Filter | None = None,
        group_code: str | Filter | None = None,
    ) -> ProductList:
        """Get all products.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            code: Filter by product code
            group_code: Filter by product group code

        Returns:
            Paginated list of products
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            code=code,
            groupCode=group_code,
        )
        response = self._get("/v1/product", params)
        return ProductList.model_validate(response.json())

    def get(self, id: int) -> Product:
        """Get a product by ID.

        Args:
            id: Product ID

        Returns:
            Full product details
        """
        response = self._get(f"/v1/product/{id}")
        return Product.model_validate(response.json())

    def create(self, product: CreateProduct) -> CreatedProduct:
        """Create a new product.

        Args:
            product: Product data

        Returns:
            Created product ID
        """
        response = self._post("/v1/product", self._model_to_dict(product))
        return CreatedProduct.model_validate(response.json())

    def update(self, id: int, product: PatchProduct) -> None:
        """Update a product.

        Args:
            id: Product ID
            product: Updated product data
        """
        self._patch(f"/v1/product/{id}", self._model_to_dict(product))

    def delete(self, id: int) -> None:
        """Delete a product.

        Args:
            id: Product ID
        """
        self._delete(f"/v1/product/{id}")

    def list_groups(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ProductGroupList:
        """Get all product groups.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip

        Returns:
            Paginated list of product groups
        """
        params = self._build_params(limit=limit, offset=offset)
        response = self._get("/v1/product/groups", params)
        return ProductGroupList.model_validate(response.json())

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[ProductListItem, None, None]:
        """Iterate through all products.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual products
        """
        return self._paginate(
            "/v1/product",
            ProductList,
            ProductListItem,
            limit=limit,
            **kwargs,
        )

    def iter_groups(self, limit: int = 100) -> Generator[ProductGroup, None, None]:
        """Iterate through all product groups.

        Args:
            limit: Items per page

        Yields:
            Individual product groups
        """
        return self._paginate(
            "/v1/product/groups",
            ProductGroupList,
            ProductGroup,
            limit=limit,
        )
