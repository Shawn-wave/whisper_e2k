import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
import torch
from datetime import datetime
import whisper
import yt_dlp
import gradio as gr
from transformers import pipeline

WHISPER_MODELS = ["large-v3", "large-v2", "large", "medium", "small", "base", "tiny"]
LANGUAGES = {
    "자동 감지": None,
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어": "zh"
}

class TranslationManager:
    def __init__(self):
        self.translator = pipeline(
            "translation",
            model="facebook/nllb-200-distilled-600M",
            tokenizer="facebook/nllb-200-distilled-600M"
        )

    def translate_text(self, text, target_lang="ko"):
        if not text or text.isspace():
            return ""
            
        text = text.strip()
        result = self.translator(
            text,
            src_lang="eng_Latn",
            tgt_lang="kor_Hang",
            max_length=512
        )
        return result[0]['translation_text'].strip()

class WhisperWebUI:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.translation_manager = TranslationManager()
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def format_timestamp(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"

    def create_subtitle(self, segments, output_format="srt", include_timestamp=True):
        content = []
        
        if include_timestamp:
            # 타임스탬프 포함 로직
            if output_format.lower() == "srt":
                for i, segment in enumerate(segments, start=1):
                    content.extend([
                        str(i),
                        f"{self.format_timestamp(segment['start'])} --> {self.format_timestamp(segment['end'])}",
                        f"{segment['text'].strip()}\n"
                    ])
            else:  # txt
                for segment in segments:
                    content.append(f"[{self.format_timestamp(segment['start'])} --> {self.format_timestamp(segment['end'])}]")
                    content.append(f"{segment['text'].strip()}\n")
        else:
            # 단락 형태로 텍스트 결합
            current_paragraph = []
            for segment in segments:
                text = segment['text'].strip()
                
                # 문장이 끝나는 부분인지 확인
                if text.endswith(('.', '!', '?', '...', '"', '"')):
                    current_paragraph.append(text)
                    if current_paragraph:
                        content.append(' '.join(current_paragraph))
                    current_paragraph = []
                else:
                    current_paragraph.append(text)
            
            # 마지막 단락 처리
            if current_paragraph:
                content.append(' '.join(current_paragraph))
        
        return '\n'.join(content)

    def process_segments(self, segments, translate_to_ko=False):
        if not translate_to_ko:
            return segments
        
        translated_segments = []
        for segment in segments:
            translated_text = self.translation_manager.translate_text(segment['text'].strip())
            translated_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': translated_text
            })
        return translated_segments

    def process_video(self, input_file, custom_filename, model_name="base", language="자동 감지",
                     output_format="srt", translate_to_en=False, translate_to_ko=False,
                     include_timestamp=True):
        try:
            if not input_file:
                return None

            # 사용자 지정 파일명 처리
            if custom_filename and custom_filename.strip():  # 공백 체크 추가
                base_filename = custom_filename.strip()
            else:
                if hasattr(input_file, 'name'):
                    base_filename = os.path.splitext(os.path.basename(input_file.name))[0]
                else:
                    base_filename = f"subtitle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 파일명에서 특수문자 제거
            base_filename = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in base_filename)
            
            temp_path = os.path.join(self.temp_dir, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
            with open(temp_path, 'wb') as f:
                f.write(input_file.read() if hasattr(input_file, 'read') else input_file)

            model = whisper.load_model(model_name).to(self.device)
            result = model.transcribe(temp_path, language=LANGUAGES[language])
            
            output_files = []
            segments = result["segments"]

            if translate_to_en:
                en_path = os.path.join(self.output_dir, f"{base_filename}_eng.{output_format.lower()}")
                with open(en_path, "w", encoding="utf-8") as f:
                    f.write(self.create_subtitle(segments, output_format, include_timestamp))
                output_files.append(en_path)

            if translate_to_ko:
                ko_segments = self.process_segments(segments, translate_to_ko=True)
                ko_path = os.path.join(self.output_dir, f"{base_filename}_kor.{output_format.lower()}")
                with open(ko_path, "w", encoding="utf-8") as f:
                    f.write(self.create_subtitle(ko_segments, output_format, include_timestamp))
                output_files.append(ko_path)

            if not translate_to_en and not translate_to_ko:
                default_path = os.path.join(self.output_dir, f"{base_filename}.{output_format.lower()}")
                with open(default_path, "w", encoding="utf-8") as f:
                    f.write(self.create_subtitle(segments, output_format, include_timestamp))
                output_files.append(default_path)

            os.remove(temp_path)
            return output_files

        except Exception as e:
            return None

    def process_youtube(self, url, custom_filename, model_name="base", language="자동 감지",
                    output_format="srt", translate_to_en=False, translate_to_ko=False,
                    include_timestamp=True):
            try:
                if not url:
                    return None

                temp_path = os.path.join(self.temp_dir, f"youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                    'outtmpl': temp_path,
                    'quiet': True
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    temp_path = f"{temp_path}.mp3"
                    
                    # 사용자 지정 파일명 처리 - 공백 체크 추가
                    if custom_filename and custom_filename.strip():
                        title = custom_filename.strip()
                    else:
                        title = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in info.get('title', 'video'))

                # 파일명에서 특수문자 제거
                title = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)

                model = whisper.load_model(model_name).to(self.device)
                result = model.transcribe(temp_path, language=LANGUAGES[language])
                
                output_files = []
                segments = result["segments"]

                if translate_to_en:
                    en_path = os.path.join(self.output_dir, f"{title}_eng.{output_format.lower()}")
                    with open(en_path, "w", encoding="utf-8") as f:
                        f.write(self.create_subtitle(segments, output_format, include_timestamp))
                    output_files.append(en_path)

                if translate_to_ko:
                    ko_segments = self.process_segments(segments, translate_to_ko=True)
                    ko_path = os.path.join(self.output_dir, f"{title}_kor.{output_format.lower()}")
                    with open(ko_path, "w", encoding="utf-8") as f:
                        f.write(self.create_subtitle(ko_segments, output_format, include_timestamp))
                    output_files.append(ko_path)

                if not translate_to_en and not translate_to_ko:
                    default_path = os.path.join(self.output_dir, f"{title}.{output_format.lower()}")
                    with open(default_path, "w", encoding="utf-8") as f:
                        f.write(self.create_subtitle(segments, output_format, include_timestamp))
                    output_files.append(default_path)

                os.remove(temp_path)
                return output_files

            except Exception as e:
                return None

    def create_ui(self):
        with gr.Blocks(title="Whisper 자막 생성기") as app:
            gr.Markdown("# Whisper AI 자막 생성기")
            
            with gr.Tabs():
                with gr.Tab("파일"):
                    input_file = gr.File(
                        label="비디오/오디오 파일",
                        file_types=["mp4", "avi", "mov", "mkv", "mp3", "wav", "m4a", "webm"],
                        type="binary"
                    )
                    
                    with gr.Row():
                        model_choice = gr.Dropdown(choices=WHISPER_MODELS, value="base", label="Whisper 모델")
                        language = gr.Dropdown(choices=list(LANGUAGES.keys()), value="자동 감지", label="입력 언어")
                    
                    with gr.Group():
                        gr.Markdown("### ⚙️옵션")
                        output_format = gr.Radio(choices=["SRT", "TXT"], value="SRT", label="출력 형식")
                        with gr.Row():
                            translate_to_en = gr.Checkbox(label="영어 출력")
                            translate_to_ko = gr.Checkbox(label="한국어 번역")
                            include_timestamp = gr.Checkbox(label="타임스탬프 포함", value=True)
                            
                    with gr.Group():
                        gr.Markdown("### 📝 파일이름")
                        custom_filename = gr.Textbox(
                            label="저장할 파일명",
                            placeholder="파일명을 입력하세요 (확장자 제외)"
                        )
                    
                    with gr.Row():
                        submit_btn_file = gr.Button("자막 생성", variant="primary")
                        stop_btn_file = gr.Button("중지", variant="secondary")
                    
                    with gr.Group():
                        gr.Markdown("### 📥 결과")
                        output_files = gr.File(label="생성된 자막 파일", file_count="multiple")

                with gr.Tab("링크"):
                    youtube_url = gr.Textbox(label="링크", placeholder="https://www.youtube.com/watch?v=...")
                    
                    with gr.Row():
                        model_choice_yt = gr.Dropdown(choices=WHISPER_MODELS, value="base", label="Whisper 모델")
                        language_yt = gr.Dropdown(choices=list(LANGUAGES.keys()), value="자동 감지", label="입력 언어")
                    
                    with gr.Group():
                        gr.Markdown("### ⚙️ 옵션")
                        output_format_yt = gr.Radio(choices=["SRT", "TXT"], value="SRT", label="출력 형식")
                        with gr.Row():
                            translate_to_en_yt = gr.Checkbox(label="영어 출력")
                            translate_to_ko_yt = gr.Checkbox(label="한국어 번역")
                            include_timestamp_yt = gr.Checkbox(label="타임스탬프 포함", value=True)
                            
                    with gr.Group():
                        gr.Markdown("### 📝 파일이름")
                        custom_filename_yt = gr.Textbox(
                            label="저장할 파일명",
                            placeholder="파일명을 입력하세요 (확장자 제외)"
                        )
                        
                    with gr.Row():
                        submit_btn_yt = gr.Button("자막 생성", variant="primary")
                        stop_btn_yt = gr.Button("중지", variant="secondary")
                    
                    with gr.Group():
                        gr.Markdown("### 📥 결과")
                        output_files_yt = gr.File(label="생성된 자막 파일", file_count="multiple")

                # 파일 처리 이벤트
                file_event = submit_btn_file.click(
                    fn=self.process_video,
                    inputs=[
                        input_file, custom_filename, model_choice, language, output_format,
                        translate_to_en, translate_to_ko, include_timestamp
                    ],
                    outputs=[output_files]
                )

                # 유튜브 처리 이벤트
                yt_event = submit_btn_yt.click(
                    fn=self.process_youtube,
                    inputs=[
                        youtube_url, custom_filename_yt, model_choice_yt, language_yt, output_format_yt,
                        translate_to_en_yt, translate_to_ko_yt, include_timestamp_yt
                    ],
                    outputs=[output_files_yt]
                )

                # 중지 버튼 이벤트
                stop_btn_file.click(fn=lambda: None, cancels=file_event)
                stop_btn_yt.click(fn=lambda: None, cancels=yt_event)

                return app

if __name__ == "__main__":
    webui = WhisperWebUI()
    app = webui.create_ui()
    app.launch()