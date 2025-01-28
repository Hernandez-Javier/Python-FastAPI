from fastapi import APIRouter, Depends, HTTPException
from api.v1.endpoints import product, inventory, order, report
from utils.dependencies import get_current_user

router = APIRouter()

#routes with jwt security
router.include_router(product.router, prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)])
router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"], dependencies=[Depends(get_current_user)])
router.include_router(order.router, prefix="/orders", tags=["Orders"], dependencies=[Depends(get_current_user)])
router.include_router(report.router, prefix="/reports", tags=["Reports"], dependencies=[Depends(get_current_user)])