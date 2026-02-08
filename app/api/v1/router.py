from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.companies import router as companies_router
from app.api.v1.users import router as users_router
from app.api.v1.trucks import router as trucks_router
from app.api.v1.dashboard import router as dashboard_router

from app.api.v1.drafts import router as drafts_router
from app.api.v1.load_drafts import router as load_drafts_router
from app.api.v1.expense_drafts import router as expense_drafts_router
from app.api.v1.fuel_drafts import router as fuel_drafts_router
from app.api.v1.inventory_event_drafts import router as inventory_event_drafts_router
from app.api.v1.settlement_drafts import router as settlement_drafts_router

from app.api.v1.review_gate import router as review_gate_router
from app.api.v1.submit_draft import router as submit_draft_router

from app.api.v1.loads import router as loads_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.fuel_transactions import router as fuel_transactions_router
from app.api.v1.settlements import router as settlements_router

from app.api.v1.inventory_items import router as inventory_items_router
from app.api.v1.inventory_locations import router as inventory_locations_router
from app.api.v1.inventory_events import router as inventory_events_router

from app.api.v1.ifta_tax_rates import router as ifta_tax_rates_router
from app.api.v1.ifta_return_drafts import router as ifta_return_drafts_router
from app.api.v1.ifta_return_state_lines import router as ifta_return_state_lines_router

from app.api.v1.fuel_cards import router as fuel_cards_router

router = APIRouter()

# Public read pages
# Core
router.include_router(health_router, tags=["health"])
router.include_router(auth_router, tags=["auth"])
router.include_router(companies_router, tags=["companies"])
router.include_router(users_router, tags=["users"])
router.include_router(trucks_router, tags=["trucks"])
router.include_router(dashboard_router, tags=["dashboard"])

# Draft engine + typed drafts
router.include_router(drafts_router, tags=["drafts"])
router.include_router(load_drafts_router, tags=["load-drafts"])
router.include_router(expense_drafts_router, tags=["expense-drafts"])
router.include_router(fuel_drafts_router, tags=["fuel-drafts"])
router.include_router(inventory_event_drafts_router, tags=["inventory-event-drafts"])
router.include_router(settlement_drafts_router, tags=["settlement-drafts"])

# Review + submit
router.include_router(review_gate_router, tags=["review-gate"])
router.include_router(submit_draft_router, tags=["submit"])

# Final truth records
router.include_router(loads_router, tags=["loads"])
router.include_router(expenses_router, tags=["expenses"])
router.include_router(fuel_transactions_router, tags=["fuel-transactions"])
router.include_router(settlements_router, tags=["settlements"])

# Inventory
router.include_router(inventory_items_router, tags=["inventory-items"])
router.include_router(inventory_locations_router, tags=["inventory-locations"])
router.include_router(inventory_events_router, tags=["inventory-events"])

# IFTA
router.include_router(ifta_tax_rates_router, tags=["ifta-tax-rates"])
router.include_router(ifta_return_drafts_router, tags=["ifta-return-drafts"])
router.include_router(ifta_return_state_lines_router, tags=["ifta-return-state-lines"])

# Fuel Cards
router.include_router(fuel_cards_router, tags=["fuel-cards"])


