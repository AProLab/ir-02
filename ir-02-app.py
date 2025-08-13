import streamlit as st
import requests
import base64


class BloodPressureAnalyzer:
    """혈압 측정 사진을 분석하는 클래스"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _encode_image(self, file_image):
        """이미지 파일을 base64로 인코딩"""
        file_image.seek(0)
        image_bytes = file_image.read()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _build_prompt(self, base64_image: str):
        """API 요청 메시지 구성"""
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                            당신은 내과 전문의입니다.
                            입력된 환자의 협압 측정 결과 사진을 보고, 환자에게 내과 전문의로써 의견을 [출력 예1] 과 같이 간단히 설명해주세요

                            [출력 예 1]

                            **최고(수축기) 혈압**: 1200mmHg
                            **최저(이완기) 혈압**: 80mmHg
                            **심박수**: 60bpm
                            
                            [여기에 최고 혈압, 최저 혈압, 심박수 관련 의견을 200자 내외로 서술]

                            입력된 사진으로 혈압 측정 결과를 인식할 수 없거나, 관련 없는 사진일 경우 [출력 예 2]와 같이 출력하세요
                            
                            [출력 예 2]
                            **죄송합니다. 인식할 수 없는 사진입니다.**
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]

    def analyze(self, file_image):
        """혈압 측정 사진 분석"""
        base64_image = self._encode_image(file_image)
        messages = self._build_prompt(base64_image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": messages
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


class BloodPressureApp:
    """혈압 분석 Streamlit UI 클래스"""
    def __init__(self):
        self.api_key = None
        self.file_image_bp = None

    def run(self):
        """Streamlit 앱 실행"""
        st.header("혈압 측정 결과 분석")
        self.api_key = st.text_input("OPENAI API KEY를 입력하세요.", type="password")
        self.file_image_bp = st.file_uploader("혈압 측정 사진만 업로드하세요!", type=['png', 'jpg', 'jpeg'])

        if self.api_key and self.file_image_bp:
            analyzer = BloodPressureAnalyzer(self.api_key)
            st.image(self.file_image_bp, width=500)

            with st.spinner("혈압 측정 결과 분석중..."):
                try:
                    result = analyzer.analyze(self.file_image_bp)
                    st.markdown(result)
                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 오류: {e}")


if __name__ == "__main__":
    app = BloodPressureApp()
    app.run()