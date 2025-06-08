# youtube_captions_collector.py

from datetime import datetime, timezone
from typing import Any, Dict

from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeCaptionsCollector:
    """
    고정된 YouTube 영상 ID에서 자막을 수집하는 클래스
    """

    def __init__(self) -> None:
        # 비트코인 분석 영상 ID 리스트
        self.video_ids = [
            "QjH-wvXpz-4",
        ]

        # 영상 메타데이터 관리
        self.video_metadata = {
            "QjH-wvXpz-4": {
                "title": "Bitcoin to $200k?! Latest 2025 BTC Price Predictions",
                "channel": "Coin Bureau",
            },
        }

    def _get_transcript(self, video_id: str) -> str:
        """영상 ID에서 자막 추출"""
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            text = " ".join([item.text for item in transcript])
            return text.strip()
        except Exception as e:
            print(f"자막 추출 실패 {video_id}: {e}")
            return ""

    def collect_captions(self) -> Dict[str, Any]:
        """모든 영상에서 자막 수집"""
        print("📺 YouTube 자막 수집 시작...")

        videos = []
        success_count = 0

        for video_id in self.video_ids:
            transcript = self._get_transcript(video_id)
            metadata = self.video_metadata.get(
                video_id,
                {"title": f"Unknown Video {video_id}", "channel": "Unknown Channel"},
            )

            video_data = {
                "video_id": video_id,
                "title": metadata["title"],
                "channel": metadata["channel"],
                "transcript_text": transcript,
                "has_transcript": len(transcript) > 0,
            }

            videos.append(video_data)

            if transcript:
                success_count += 1
                print(f"✅ {video_id}: {len(transcript)} 문자")
            else:
                print(f"❌ {video_id}: 실패")

        result = {
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_videos": len(self.video_ids),
            "successful_collections": success_count,
            "videos": videos,
        }

        print(f"📺 수집 완료: {success_count}/{len(self.video_ids)}개 성공")
        return result


if __name__ == "__main__":
    collector = YouTubeCaptionsCollector()
    result = collector.collect_captions()

    print("\n=== 결과 ===")
    for video in result["videos"]:
        status = "✅" if video["has_transcript"] else "❌"
        print(f"{status} {video['channel']} - {video['title']} ({video['video_id']})")
