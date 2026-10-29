#!/usr/bin python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify, Response
import os
import tempfile
import PyPDF2
import docx
import pandas as pd
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import openai
import io
import csv
import re
import sys
import requests
import base64
import json
import openai
from volcengine.visual.VisualService import VisualService
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    TextLoader,
    UnstructuredExcelLoader
)
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# 配置OpenAI API密钥
# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls', 'csv'}
OCR_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
OCR_API_URL = "https://ocr.volcengineapi.com"
# Credentials must be supplied through the environment, never committed to source.
API_KEY = os.getenv("VOLCENGINE_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("VOLCENGINE_ACCESS_KEY_SECRET")
LLM_KEY = os.getenv("LLM_API_KEY")
LLM_URL = os.getenv(
    "LLM_URL",
    "https://ark.cn-beijing.volces.com/api/v3",
)
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-1-flash")

def require_config(value, name):
    """Return a configured value or raise a clear configuration error."""
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class FileSummer:
    def __init__(self):
        pass
    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def extract_text_from_pdf(self,file_path):
        """从PDF文件中提取文本，支持扫描版PDF"""
        text = ""
        try:
            # 首先尝试直接提取文本
            pdf_reader = PyPDF2.PdfReader(file_path)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            # 如果提取的文本很少，可能是扫描版PDF，尝试OCR
            if len(text.strip()) < 100:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                    text += page_text + "\n"
        except Exception as e:
            text = f"PDF处理错误: {str(e)}"

        return text
    def extract_text_from_file(self,file_path):
        """使用LangChain从文件中提取文本"""
        file_extension = file_path.split('.')[-1].lower()
        logger.info("filename:"+file_path)
        try:
            if file_extension == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == 'docx':
                loader = Docx2txtLoader(file_path)
            elif file_extension == 'txt':
                loader = TextLoader(file_path)
            elif file_extension in ['xlsx', 'xls']:
                loader = UnstructuredExcelLoader(file_path)
            elif file_extension == 'csv':
                loader = CSVLoader(file_path)
            else:
                return "不支持的文件类型"

            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            return "\n".join([doc.page_content for doc in texts])
        except Exception as e:
            return f"文件处理错误: {str(e)}"
    def extract_text_from_docx(self,file_path):
        """从Word文件中提取文本"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            return f"Word处理错误: {str(e)}"

    def extract_text_from_txt(self,file_path):
        """从TXT文件中提取文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except Exception as e:
                return f"TXT处理错误: {str(e)}"

    def extract_text_from_excel(self,file_path):
        """从Excel文件中提取文本"""
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    text = "\n".join([", ".join(row) for row in rows])
            else:
                df = pd.read_excel(file_path)
                text = df.to_string(index=False)
            return text
        except Exception as e:
            return f"Excel处理错误: {str(e)}"

    # def extract_text_from_file(file_path):
    #     """根据文件类型提取文本"""
    #     file_extension = file_path.split('.')[-1].lower()
    #
    #     if file_extension in ['pdf']:
    #         return extract_text_from_pdf(file_path)
    #     elif file_extension in ['docx', 'doc']:
    #         return extract_text_from_docx(file_path)
    #     elif file_extension in ['txt']:
    #         return extract_text_from_txt(file_path)
    #     elif file_extension in ['xlsx', 'xls', 'csv']:
    #         return extract_text_from_excel(file_path)
    #     else:
    #         return "不支持的文件类型"

    def summarize_with_ai(self,text):
        """使用OpenAI API对文本进行总结，并流式返回结果"""
        try:
            # 如果文本太长，截取前面部分
            if len(text) > 10000:
                text = text[:10000] + "...(内容已截断)"
            # client = OpenAI(
            #     base_url="http://oneapi.dev.service.yuaiweiwu.com/v1",
            #     default_headers={
            #         "source-sn": "aienglish",
            #     }
            # )
            # modelName = "aienglish-doubao-1.5-pro-256K-250115"
            optimized_prompt = f"""
            请按以下规范处理文档内容：
            **文档内容**:
            {text}

            **处理要求**:
            1. 语言匹配：
               - 输出语言必须与文档语言类型完全一致（中文文档→中文输出，英文文档→英文输出）
            2. 内容结构：
               ```markdown
               # 文档总结分析

               ## 关键信息提取
               - 使用无序列表呈现（每条信息前加`•`）
               - 包含数据指标/专有名词/核心事实

               ## 主要观点归纳
               - 分二级标题呈现
               - 每个观点包含<观点标签>和观点阐述
                 `• [理论框架]: 描述内容...`

               ## 结论梳理
               - 使用数字编号列表
               - 区分直接结论与推导结论
               """
            client = OpenAI(
                api_key=require_config(LLM_KEY, "LLM_API_KEY"),
                base_url=LLM_URL,
            )
            modelName = LLM_MODEL

            response = client.chat.completions.create(
                model=modelName,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档分析助手，请对以下文档内容进行全面的总结和分析。"},
                    {"role": "user", "content": optimized_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            logger.info("完整响应内容：", response)
            logger.info("返回的摘要：", response.choices[0].message.content)

            return response.choices[0].message.content
        except Exception as e:
            return f"AI分析错误: {str(e)}"

class OCR_Qustion:
    def __init__(self):
        pass
    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in OCR_ALLOWED_EXTENSIONS

    def ocr_image(self,image_path):
        try:
            visual_service = VisualService()
            # call below method if you dont set ak and sk in $HOME/.volc/config
            visual_service.set_ak(require_config(API_KEY, "VOLCENGINE_ACCESS_KEY_ID"))
            visual_service.set_sk(require_config(SECRET_KEY, "VOLCENGINE_ACCESS_KEY_SECRET"))
            # visual_service.set_host('host')
            action = "OCRNormal"
            version = "2020-08-26"
            visual_service.set_api_info(action, version)

            # below shows the sdk usage for all common apis,
            # if you cannot find the needed one, please check other example files in the same dir
            # or contact us for further help
            form = dict()
            form["image_base64"] = base64.b64encode(open(image_path,'rb').read()).decode()
            resp = visual_service.ocr_api(action, form)
            text = resp['data']['line_texts']
            if not text:
                logger.info("OCR 识别未返回有效文字。")
            return "\n".join(text)
        except FileNotFoundError:
            logger.info(f"未找到图像文件: ")
            return None
        except requests.RequestException as e:
            logger.info(f"OCR 请求发生错误: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.info(f"解析 OCR 响应时发生错误: {e}")
            return None


    # 调用 OpenAI API 解答问题

    def solve_question(self,question):
        optimized_prompt = f"""
            请严格按以下要求回答问题：
            **问题**: {question}

            **要求**:
            1. 语言一致性：必须使用与问题完全相同的语言类型返回答案。
            2. 内容格式：
               - 使用标准 Markdown 语法和katex 数学公式。
               - 数学公式必须严格使用 `$$...$$` 或  `$...$`包裹的完整 LaTeX 表达式，禁止使用其他形式（如 `\\[ ... \\]`、`\\( ... \\)` 或其他非标准格式）。
               - 禁止使用非标准格式（如代码块包裹公式、图片代替公式等）。
            3. 响应规范：
               - 答案必须包含思考过程。
               - 严格禁止添加免责声明、建议或其他任何额外内容。
               - 不要添加任何额外的内容，如“用 Markdown 格式表示如下”或“```markdown```”等。
            """
        logger.info(question)
        if not question:
            return None
        try:
            openaiClient = openai.Client(
                base_url=LLM_URL,
                api_key=require_config(LLM_KEY, "LLM_API_KEY"),
            )
            response = openaiClient.chat.completions.create(
                model=LLM_MODEL,  # 可以根据需求更换为其他模型，如 gpt-4
                messages=[
                    {"role": "user", "content": optimized_prompt}
                ]
            )
            answer = response.choices[0].message.content
            #.replace("`$$","`$$").replace("$$`","$$").replace("$$","$").replace("$", "$$"))
            return answer
        except Exception as e:
            logger.info(f"发生未知错误: {e}")
            return None



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'summary': '没有文件部分'})
    file = request.files['file']

    if file.filename == '':
        return jsonify({'summary': '没有选择文件'})

    fileSummer = FileSummer()
    if file and fileSummer.allowed_file(file.filename):
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        # 提取文本
        extracted_text = fileSummer.extract_text_from_file(temp_path)

        # 使用AI总结
        summary = fileSummer.summarize_with_ai(extracted_text)

        # 删除临时文件
        os.remove(temp_path)
        os.rmdir(temp_dir)

        return jsonify({
            'filename': file.filename,
            'summary': summary
        })

    return jsonify({'summary': '不支持的文件类型'})
@app.route('/ocr', methods=['POST'])
def ocr():
    # 进行 OCR 识别
    if 'file' not in request.files:
        return jsonify({'summary': '没有文件部分'})
    file = request.files['file']

    if file.filename == '':
        return jsonify({'summary': '没有选择文件'})

    logger.info(file.filename)

    ocr_Qustion = OCR_Qustion()
    if file and ocr_Qustion.allowed_file(file.filename):
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        # 提取文本
        question = ocr_Qustion.ocr_image(temp_path)
        # 使用AI总结
        if question:
            # 调用 OpenAI 解答问题
            answer = ocr_Qustion.solve_question(question)
            if answer:
                logger.info(f"问题: {question}")
                logger.info(f"答案: {answer}")
            else:
                logger.info("未能获取到问题的解答，请检查网络或 OpenAI API 配置。")
        else:
            logger.info("未识别到文字，请检查图片或 OCR 配置。")
            # 删除临时文件
        os.remove(temp_path)
        os.rmdir(temp_dir)

        return jsonify({
            'filename': file.filename,
            'summary': answer
        })
    return jsonify({'summary': '不支持的文件类型'})
@app.route('/upload1/file', methods=['POST'])
def uploadfile():
    logger.info(f"json:{request.get_json()}")
    logger.info(f"data:{request.get_data()}")
    if 'path' not in request.get_json():
        return jsonify({'summary': '没有文件部分'})
    path = request.get_json().get("path")

    fileSummer = FileSummer()
    if fileSummer.allowed_file(path):
        # 提取文本
        extracted_text = fileSummer.extract_text_from_file(path)
        # 使用AI总结
        summary = fileSummer.summarize_with_ai(extracted_text)
        return jsonify({
            'filename': path,
            'summary': summary
        })

    return jsonify({'summary': '不支持的文件类型'})
@app.route('/upload1/ocr', methods=['POST'])
def uplodocr():
    logger.info(f"json:{request.get_json()}")
    logger.info(f"data:{request.get_data()}")
    if 'path' not in request.get_json():
        return jsonify({'summary': '没有文件部分'})
    path = request.get_json().get("path")
    ocr_Qustion = OCR_Qustion()
    if ocr_Qustion.allowed_file(path):
        question = ocr_Qustion.ocr_image(path)
        # 使用AI总结
        if question:
            # 调用 OpenAI 解答问题
            answer = ocr_Qustion.solve_question(question)
            if answer:
                logger.info(f"问题: {question}")
                logger.info(f"答案: {answer}")
            else:
                logger.info("未能获取到问题的解答，请检查网络或 OpenAI API 配置。")
        else:
            logger.info("未识别到文字，请检查图片或 OCR 配置。")
            # 删除临时文件
        return jsonify({
            'filename': path,
            'summary': answer
        })
    return jsonify({'summary': '不支持的文件类型'})
if __name__ == '__main__':
    logger.info("Starting Flask application...")  # 检查这条消息是否显示
    app.run(debug=True, use_reloader=False)
