from pathlib import Path
import re
import time

import pytest


@pytest.mark.e2e
@pytest.mark.slow
def test_streamlit_user_can_upload_csv_and_start_analysis(page):
    sample_file = str(Path("tests/e2e/test_data/sample_comments.csv").resolve())

    page.goto("http://127.0.0.1:8501", wait_until="networkidle")
    page.wait_for_timeout(5000)

    # جرّب التعامل مع خيار Drive فقط إذا ظهر
    possible_drive_labels = [
        "استخدم ملف المشروع الموجود في Drive",
        "Use project file from Drive",
        "Drive",
    ]

    for label in possible_drive_labels:
        locator = page.get_by_text(label, exact=False)
        if locator.count() > 0:
            try:
                locator.first.click()
                page.wait_for_timeout(1500)
                break
            except Exception:
                pass

    file_input = page.locator('input[type="file"]')
    if file_input.count() == 0:
        page.screenshot(path="e2e_no_file_input.png", full_page=True)
        body_text = page.locator("body").inner_text()
        raise AssertionError(
            "لم يتم العثور على عنصر رفع الملف.\n\n"
            f"محتوى الصفحة الظاهر:\n{body_text[:3000]}"
        )

    file_input.first.set_input_files(sample_file)
    page.wait_for_timeout(1500)

    numeric_fields = [
        ("الحد الأدنى لتعليقات المنشور", "1"),
        ("الحد الأدنى لحجم الموضوع", "5"),
        ("sample size", "10"),
        ("min comments", "1"),
        ("min topic size", "5"),
    ]

    for label, value in numeric_fields:
        field = page.get_by_role("spinbutton", name=re.compile(label, re.IGNORECASE))
        if field.count() > 0:
            try:
                field.first.fill(value)
                page.wait_for_timeout(500)
            except Exception:
                pass

    button_names = [
        "تشغيل التحليل",
        "ابدأ التحليل",
        "تحليل",
        "Run Analysis",
        "Start Analysis",
        "Analyze",
    ]

    clicked = False
    for name in button_names:
        button = page.get_by_role("button", name=re.compile(name, re.IGNORECASE))
        if button.count() > 0:
            try:
                button.first.click()
                clicked = True
                break
            except Exception:
                pass

    if not clicked:
        page.screenshot(path="e2e_no_button.png", full_page=True)
        body_text = page.locator("body").inner_text()
        raise AssertionError(
            "لم يتم العثور على زر التحليل.\n\n"
            f"محتوى الصفحة الظاهر:\n{body_text[:3000]}"
        )

    expected_keywords = [
        "الخلاصة التنفيذية",
        "نتائج",
        "المواضيع",
        "تحليل",
        "Topic",
        "Topics",
        "Results",
    ]

    deadline = time.time() + 120
    while time.time() < deadline:
        body_text = page.locator("body").inner_text()
        if any(word in body_text for word in expected_keywords):
            return
        page.wait_for_timeout(2000)

    page.screenshot(path="e2e_result_timeout.png", full_page=True)
    body_text = page.locator("body").inner_text()
    raise AssertionError(
        "لم تظهر نتيجة متوقعة بعد تشغيل التحليل.\n\n"
        f"محتوى الصفحة الظاهر:\n{body_text[:4000]}"
    )
