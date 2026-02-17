from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# --- مدل داده ورودی ---
class UnitInput(BaseModel):
    """
    مدل داده برای دریافت ابعاد یونیت و ضخامت متریال از کاربر.
    همه ابعاد بر حسب میلی‌متر (mm) فرض شده‌اند.
    """
    width: int          # عرض خارجی نهایی یونیت (مثلاً 600)
    height: int         # ارتفاع خارجی نهایی یونیت (مثلاً 850)
    depth: int          # عمق خارجی نهایی یونیت (مثلاً 550)
    material_thickness: int # ضخامت متریال (مثلاً 16 یا 18)

# --- راه‌اندازی اپلیکیشن ---
app = FastAPI(
    title="Advanced Cabinet Unit Calculator",
    description="FastAPI service to calculate cut list based on dimensions and material thickness for cabinet making."
)

@app.get("/")
def home():
    """نقطه پایانی برای بررسی سلامت سرور."""
    return {"status": "ok", "message": "Advanced Cabinet Unit Calculator is running successfully."}

# --- نقطه پایانی اصلی محاسبه ---
@app.post("/calculate")
def calculate(unit: UnitInput) -> Dict[str, Any]:
    """
    محاسبه لیست قطعات (Cut List) برای یک کابینت زمینی استاندارد.
    """
    
    t = unit.material_thickness
    
    # 1. محاسبه ابعاد داخلی برای پنل‌های افقی (سقف و کف)
    # عرض پنل افقی = عرض کلی - (2 * ضخامت پنل جانبی)
    inner_width = unit.width - (2 * t)
    
    # عمق پنل افقی = عمق کلی - (ضخامت پنل پشتی، اگر در شیار قرار گیرد)
    # برای سادگی، عمق را برابر با عمق ورودی در نظر می‌گیریم و فرض می‌کنیم پنل پشتی به موازات عمق نصب می‌شود.
    
    panels: Dict[str, List[Dict[str, Any]]] = {
        "side_panels": [
            {"name": "پنل جانبی چپ", "width": unit.depth, "height": unit.height},
            {"name": "پنل جانبی راست", "width": unit.depth, "height": unit.height}
        ],
        "horizontal_panels": [
            {"name": "سقف", "width": inner_width, "depth": unit.depth},
            {"name": "کف", "width": inner_width, "depth": unit.depth}
        ],
        "back_panel": [
            # پنل پشت با عرض کامل یونیت برای پوشش فضای خالی در نظر گرفته می‌شود.
            {"name": "پنل پشت", "width": unit.width, "height": unit.height}
        ]
    }

    # --- محاسبه جزئیات بیشتر (اختیاری اما مفید) ---
    # اضافه کردن یک لبه برای کف یونیت (مثلاً برای پایه‌ها)
    base_support = {
        "name": "لبه زیرین (Base Support)", 
        "length": inner_width, 
        "count": 1
    }

    return {
        "input_received": unit.model_dump(),
        "calculated_parts": {
            "cut_list_pieces": panels,
            "base_support": base_support
        },
        "notes": f"محاسبات بر اساس ضخامت متریال {t}mm و ابعاد خارجی انجام شد. سقف و کف بر اساس عرض داخلی ({inner_width}mm) محاسبه شدند."
    }

# --- نکته مهم برای اجرا ---
# برای اجرای این سرور، شما نیاز به نصب FastAPI و Uvicorn دارید:
# pip install fastapi "uvicorn[standard]"
# سپس دستور زیر را در ترمینال اجرا کنید:
# uvicorn main:app --reload
