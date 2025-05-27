# Team Copilot

<img src="media/ui.png" alt="User interface" width="500">

Team Copilot is a chatbot application that aims to help the members of a team do their
work by managing a set of PDF documents and replying to questions about the documents.
The application is written in Python and has a FastAPI based API with endpoints for
authentication, uploading documents and making questions.

The application has a **LangGraph** based agent that manages the chats and uses a remote
**embedding model** from [Voyage AI](https://www.voyageai.com) and a remote
**LLM model** from [Anthropic](https://www.anthropic.com). Therefore, a Voyage AI API
key and an Anthropic API key are required to run the agent.

The application uses the **PyMuPDF** and **PyTesseract** Python libraries to extract the
text of the PDF documents. PyMuPDF is used to extract plain text and images and
PyTesseract is used to extract text from the previously extracted images through OCR
(Optical Character Recognition). The extracted text of each document is stored in a
**PostgreSQL** database configured as a vector database with the **PgVector** PostgreSQL
extension.

## Data Flow Diagram

```mermaid
flowchart TD
    User([User]) <--> API[FastAPI API]
    
    API --> |PDF file & data| DocUpload[1\. Document Upload]
    API --> |Question text| ChatQuestion[2\. Chat Question]

    DocUpload --> |PDF file| TextExt[1\.1\. Text Extraction with PyMuPDF]
    DocUpload --> |PDF file| ImgExt[1\.2\. Images Extraction with PyMuPDF]

    ImgExt --> |Images| OcrTextExt[1\.3\. OCR Text Extraction with PyTesseract]

    TextExt --> |Text| TextConcat[1\.4\. Text Concatenation]
    OcrTextExt --> |Text| TextConcat

    TextConcat --> |Text| TextSplit[1\.5\. Text Split into Chunks]

    TextSplit --> |Text chunks| TextEmb[1\.6\. / 2\.2\. Voyage AI API]
    TextEmb --> |Document information| Db[(1\.7\. PostgreSQL with PgVector)]
    TextEmb --> |Chunk texts| Db
    TextEmb --> |Chunk embeddings | Db
    
    ChatQuestion --> |Question text| Agent[2\.1\. / 2\.3\. / 2\.5\. / 2\.7\. LangGraph Agent]
    Agent --> |Question text| TextEmb
    TextEmb --> |Question embedding| Agent
    

    Agent --> |Question embedding|VecSearch[2\.4\. Search for Most Similar Chunks]
    VecSearch --> |Question embedding| Db
    Db --> |Most similar chunk texts| VecSearch
    VecSearch --> |Most similar chunk texts| Agent

    Agent --> |Question text with most similar chunk texts as context| Llm[2\.6\. Anthropic API]
    Llm --> |Streaming AI-generated answer text| Agent
    Agent --> |Streaming AI-generated answer text| API
```

## Document Processing Flow

Each time a PDF document is uploaded to the application, the following steps are
performed:

1. A new document record is inserted in the database, with "pending" status.
2. The PDF document is uploaded to a temporary path in the file system.
3. The status of the database document record is updated to "processing".
4. The text and images of the document are extracted with PyMuPDF.
5. For each extracted image, if the image contains text, the text is extracted with
   PyTesseract.
6. The complete extracted text is split into chunks.
7. For each text chunk, the embedding (vector of numbers) of the chunk is generated
   with the remote Voyage AI embedding model.
8. For each text chunk, a new document chunk record is inserted in the database,
   including the chunk text and the chunk embedding.
9. The status of the database document record is updated to "completed". If any error
   happens during the previous steps, the status is updated to "failed".
10. The uploaded PDF document is deleted.

## Question Answering Flow

Each time a question is asked to the application, the following steps are performed:

1. The agent converts the question text to an embedding (vector of numbers) with the
   remote Voyage AI embedding model.
2. The agent searches for the embeddings of the document chunks stored in the database
   that are the most similar embeddings to the question embedding. The search is done by
   calculating the cosine distance between two vectors, where the vectors are any of the
   document chunk embeddings and the question embedding. The smaller the cosine distance
   between two vectors is, the more similar the vectors are.
3. The agent retrieves the text of the most similar document chunks found and
   concatenates it into a single text.
4. The agent sends the question text, and the text of the most similar document chunks
   found as a context, to the remote Anthropic LLM model.
5. The agent returns the response of the LLM model in streaming, which is returned by
   the application as well.

## Documentation User Interface Screenshots

<img src="media/doc_ui_1.png" alt="Documentation user interface - Header" width="500">
<img src="media/doc_ui_2.png" alt="Documentation user interface - Health endpoints" width="500">
<img src="media/doc_ui_3.png" alt="Documentation Uuser interfaceI - Authentication endpoints" width="500">
<img src="media/doc_ui_4.png" alt="Documentation user interface - Users endpoints" width="500">
<img src="media/doc_ui_5.png" alt="Documentation user interface - Documents endpoints" width="500">
<img src="media/doc_ui_6.png" alt="Documentation user interface - Chat endpoints" width="500">
<img src="media/doc_ui_7.png" alt="Documentation user interface - Default endpoints" width="500">
