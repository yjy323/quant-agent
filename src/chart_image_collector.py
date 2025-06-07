# chart_image_collector.py

import base64
import io
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config


class ChartType(Enum):
    CANDLESTICK = "candlestick"
    LINE = "line"
    INDICATOR = "indicator"


@dataclass
class ChartImageMetadata:
    image_id: str
    timestamp: str
    chart_type: ChartType
    timeframe: str  # "1m"
    symbol: str  # "KRW-BTC"
    price_info: Dict[str, Any]
    capture_duration_ms: int  # 순서 변경: 기본값이 없는 인자를 먼저 선언
    image_size: Optional[Dict[str, int]] = None


class ChartImageCollector:
    """
    업비트 차트 이미지를 Selenium으로 수집하고 전처리하는 클래스
    60초 간격 매매를 위한 고속 차트 캡처 최적화
    """

    def __init__(self) -> None:
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: WebDriverWait = WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT)
        self.page_loaded: bool = False
        self.upbit_chart_url: str = Config.UPBIT_CHART_URL
        self._initialize_driver()

    def _initialize_driver(self) -> None:
        """Selenium WebDriver를 초기화합니다."""
        if self.driver is None:
            print("⚙️ WebDriver 초기화 중...")
            try:
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"]
                )
                options.add_experimental_option("useAutomationExtension", False)

                if Config.SELENIUM_HEADLESS:
                    options.add_argument("--headless")
                    print("➡️ 헤드리스 모드로 실행됩니다.")
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa: E501
                )

                self.driver = webdriver.Chrome(options=options)
                self.driver.set_page_load_timeout(Config.SELENIUM_TIMEOUT)
                print("✅ WebDriver 초기화 완료.")
            except WebDriverException as e:
                print(f"❌ WebDriver 초기화 실패: {e}")
                self.driver = None
                raise

    def load_page(self) -> bool:
        """업비트 차트 페이지를 로드하고 주요 요소가 나타날 때까지 대기합니다."""
        if self.driver is None:
            print("❌ WebDriver가 초기화되지 않았습니다. 페이지를 로드할 수 없습니다.")
            return False

        if self.page_loaded:
            print(
                "ℹ️ 페이지가 이미 로드되었습니다. 새로고침하려면 refresh_chart()를 사용하세요."
            )
            return True

        print(f"🌐 {self.upbit_chart_url} 페이지 로드 중...")
        try:
            self.driver.get(self.upbit_chart_url)

            self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".cq-chart-container.break-lg")
                )
            )
            print("✅ 차트 컨테이너 로드 확인.")

            self.wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "cq-hu-static"))
            )
            print("✅ 가격 정보 영역 로드 확인.")

            self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ciq-period")))
            print("✅ 차트 주기 드롭다운 버튼 활성화 확인.")

            self.page_loaded = True
            print("✅ 페이지 로드 완료.")
            return True
        except TimeoutException as e:
            print(
                f"❌ 페이지 로드 오류:{self.upbit_chart_url} - 필수 요소가 나타나지 않거나 "
                f"클릭 가능하지 않습니다. 상세: {e}"
            )
            self.page_loaded = False
            return False
        except WebDriverException as e:
            print(f"❌ 페이지 로드 중 WebDriver 오류 발생: {e}")
            self.page_loaded = False
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 페이지 로드 오류: {e}")
            self.page_loaded = False
            return False

    def _set_1minute_timeframe(self) -> bool:
        """차트 주기를 1분봉으로 설정합니다."""
        if not self.page_loaded or self.driver is None:
            print("❌ 페이지가 로드되지 않아 1분봉 설정 불가.")
            return False

        print("⏱️ 차트 주기를 1분봉으로 설정 중...")
        try:
            period_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ciq-period"))
            )
            ActionChains(self.driver).move_to_element(period_dropdown).click().perform()
            print("➡️ 'ciq-period' 드롭다운 클릭.")

            one_min_option = self.wait.until(
                EC.element_to_be_clickable(
                    By.XPATH,
                    "//div[contains(@class, 'ciq-dropdowns')]//cq-menu[contains(@class, 'ciq-period')]//cq-item[.//translate[text()='1분']]",  # noqa: E501
                )
            )
            ActionChains(self.driver).move_to_element(one_min_option).click().perform()
            print("✅ '1분' 차트 주기 설정 완료.")

            time.sleep(2)
            return True
        except (
            NoSuchElementException,
            TimeoutException,
            ElementNotInteractableException,
        ) as e:
            print(f"❌ 1분봉 설정 실패 (요소 찾기 또는 상호작용 오류): {e}")
            return False
        except Exception as e:
            print(f"❌ 1분봉 설정 중 예상치 못한 오류: {e}")
            return False

    def _capture_chart_area(self) -> Optional[bytes]:
        """지정된 차트 영역을 캡처하고 PNG 바이트로 반환합니다."""
        if not self.page_loaded or self.driver is None:
            print("❌ 페이지가 로드되지 않아 차트 영역 캡처 불가.")
            return None

        print("📸 차트 영역 캡처 중...")
        try:
            chart_container = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".cq-chart-container.break-lg")
                )
            )
            screenshot_bytes = chart_container.screenshot_as_png
            print("✅ 차트 영역 캡처 완료.")
            from typing import Optional, cast

            return cast(Optional[bytes], screenshot_bytes)
        except (NoSuchElementException, TimeoutException) as e:
            print(f"❌ 차트 컨테이너 찾기 실패 또는 오류: {e}")
            return None
        except WebDriverException as e:
            print(f"❌ 차트 영역 캡처 중 WebDriver 오류: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 차트 영역 캡처 오류: {e}")
            return None

    def _extract_price_info_from_dom(self) -> Dict[str, Any]:
        """
        cq-hu-static 하위에서 가격 정보 (현재가, 고가, 저가, 거래량 등)를 추출합니다.
        제공된 HTML 구조를 기반으로 정확하게 파싱합니다.
        """
        price_info: Dict[str, Any] = {}
        if not self.page_loaded or self.driver is None:
            print("❌ 페이지가 로드되지 않아 가격 정보 추출 불가.")
            return price_info

        print("📊 가격 정보 추출 중...")
        try:
            hu_static_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "cq-hu-static"))
            )

            price_tag_map = {
                "current_price": ("cq-hu-price", "현재가"),
                "open_price": ("cq-hu-open", "시가"),
                "close_price": ("cq-hu-close", "종가"),
                "volume": ("cq-hu-volume", "거래량"),
                "high_price": ("cq-hu-high", "고가"),
                "low_price": ("cq-hu-low", "저가"),
            }

            for key, (tag_name, display_name) in price_tag_map.items():
                try:
                    element = hu_static_element.find_element(By.TAG_NAME, tag_name)
                    price_info[key] = float(element.text.replace(",", ""))
                except (NoSuchElementException, ValueError):
                    price_info[key] = 0.0
                    print(f"⚠️ {display_name} 추출 실패.")

            print("✅ 가격 정보 추출 완료.")
        except (NoSuchElementException, TimeoutException) as e:
            print(f"❌ cq-hu-static 요소 또는 그 하위 요소 찾기 실패: {e}")
        except Exception as e:
            print(f"❌ 가격 정보 추출 중 예상치 못한 오류 발생: {e}")

        return price_info

    def collect_1m_chart(self) -> Optional[Dict[str, Any]]:
        """
        업비트 BTC/KRW 1분봉 차트 이미지를 캡처하고 메타데이터를 추출합니다.
        """
        start_time = time.time()
        print("🚀 1분봉 차트 및 메타데이터 수집 시작...")

        try:
            if not self.page_loaded and not self.load_page():
                print("❌ 페이지 로드 실패, 차트 수집 중단.")
                return None

            if not self._set_1minute_timeframe():
                print("❌ 1분봉 전환 실패, 차트 수집 중단.")
                return None

            chart_image_bytes = self._capture_chart_area()
            if chart_image_bytes is None:
                print("❌ 차트 이미지 캡처 실패, 차트 수집 중단.")
                return None

            image_buffer = io.BytesIO(chart_image_bytes)
            img = Image.open(image_buffer)

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            encoded_image_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

            image_width, image_height = img.size
            image_size_info = {"width": image_width, "height": image_height}

            price_info = self._extract_price_info_from_dom()

            end_time = time.time()
            capture_duration_ms = int((end_time - start_time) * 1000)

            metadata = ChartImageMetadata(
                image_id=f"chart_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                timestamp=datetime.now().isoformat(),
                chart_type=ChartType.CANDLESTICK,
                timeframe="1m",
                symbol=Config.TICKER,
                price_info=price_info,
                capture_duration_ms=capture_duration_ms,
                image_size=image_size_info,
            )

            print(f"✅ 1분봉 차트 및 메타데이터 수집 완료 ({capture_duration_ms}ms)")
            return {
                "chart_image_base64": encoded_image_string,
                "metadata": asdict(metadata),
            }

        except Exception as e:
            print(f"❌ 차트 수집 전체 실패: {e}")
            return None

    def refresh_chart(self) -> bool:
        """
        차트 새로고침 (새로운 1분봉 업데이트용)
        전체 페이지 새로고침 대신, 차트 데이터만 업데이트되도록 시도합니다.
        """
        if not self.page_loaded or self.driver is None:
            print("❌ 페이지가 로드되지 않아 차트 새로고침 불가.")
            return False

        print("🔄 차트 새로고침 시도 중...")
        try:
            if self._set_1minute_timeframe():
                print("🔄 차트 새로고침 (1분봉 재선택) 완료.")
                time.sleep(1)
                return True
            else:
                print("❌ 차트 새로고침 (1분봉 재선택) 실패.")
                return False

        except Exception as e:
            print(f"❌ 차트 새로고침 실패: {e}")
            return False

    def close_driver(self) -> None:
        """WebDriver 정리"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.page_loaded = False
                print("🚮 WebDriver 종료 완료")
        except Exception as e:
            print(f"⚠️ WebDriver 종료 중 오류: {e}")

    def __del__(self) -> None:
        """소멸자: 자동 정리"""
        self.close_driver()


# 사용 예시 및 테스트
if __name__ == "__main__":
    print("--- ChartImageCollector 테스트 시작 ---")

    collector = ChartImageCollector()

    try:
        result = collector.collect_1m_chart()

        if result:
            print("\n--- 차트 수집 결과 ---")
            print("✅ 차트 수집 성공!")
            print(f"메타데이터: {result['metadata']}")

            if "chart_image_base64" in result:
                try:
                    img_data = base64.b64decode(result["chart_image_base64"])
                    with open("captured_chart.png", "wb") as f:
                        f.write(img_data)
                    print(
                        "➡️ 캡처된 차트 이미지가 'captured_chart.png'로 저장되었습니다."
                    )
                except Exception as e:
                    print(f"❌ 캡처 이미지 파일 저장 실패: {e}")

        else:
            print("❌ 차트 수집 실패.")

    finally:
        collector.close_driver()
        print("--- ChartImageCollector 테스트 완료 ---")
