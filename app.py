import os
import cv2
from fpdf import FPDF
from yt_dlp import YoutubeDL
import gradio as gr
import tempfile

def process_video(url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            screenshot_folder = os.path.join(tmpdir, "screenshots")
            os.makedirs(screenshot_folder, exist_ok=True)

            # Step 1: Download the YouTube video
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': video_path,
                'merge_output_format': 'mp4'
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Step 2: Capture screenshots every 10 seconds
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            interval = int(fps * 10)
            image_paths = []
            count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % interval == 0:
                    image_path = os.path.join(screenshot_folder, f"frame_{count}.jpg")
                    cv2.imwrite(image_path, frame)
                    image_paths.append(image_path)
                    count += 1

            cap.release()

            # Step 3: Convert to PDF
            pdf = FPDF()
            for img_path in image_paths:
                pdf.add_page()
                pdf.image(img_path, x=10, y=10, w=190)

            pdf_path = os.path.join(tmpdir, "video_screenshots.pdf")
            pdf.output(pdf_path)

            return pdf_path
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio UI
gr.Interface(
    fn=process_video,
    inputs=gr.Textbox(label="📺 Paste YouTube Video URL", placeholder="https://youtu.be/your-video-id"),
    outputs=gr.File(label="📄 Download Your Screenshot PDF"),
    title="🎬 YouTube to Screenshot PDF Converter",
    description="Paste a YouTube URL, and this app will capture screenshots every 10 seconds and convert them into a downloadable PDF!",
    theme="default"
).launch()
