import json
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from transformers import pipeline

# Load text-generation pipeline (GPT-2 in this case)
text_generator = pipeline('text-generation', model='gpt2')
# text_generator = pipeline('text-generation', model='gpt2-large')
# text_generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B') 
# text_generator = pipeline('text-generation', model='EleutherAI/gpt-j-6B')
# text_generator = pipeline('text2text-generation', model='t5-large')


def verify_book(book_name, author_name):
    """Verify if the book exists using Google Books API."""
    google_books_url = f'https://www.googleapis.com/books/v1/volumes?q={book_name}+inauthor:{author_name}&key={settings.GOOGLE_BOOKS_API_KEY}'
    response = requests.get(google_books_url)
    result = response.json()
    return 'items' in result and len(result['items']) > 0

def generate_prompt(data):
    """Generate a refined prompt for text generation."""
    prompt = (
        # f"Create a detailed explanation about {data['topic']} based on the book {data['bookName']} by {data['authorName']}. The explanation should include the important elements mentioned in the description: {data['description']}. Use content from the book as a reference to explain the topic thoroughly and academically. "
        f"Generate an in-depth explanation on {data['topic']}, making sure to address all the aspects outlined in the description: {data['description']}. Use {data['bookName']} by {data['authorName']} as the primary reference, and ensure your arguments are supported by key concepts from the book. Focus on writing in a scholarly tone. "
        # f"Write an academic essay on the topic of {data['topic']} using information from the book {data['bookName']} by {data['authorName']}. In your essay, please include the following points as described in the description: {data['description']}. Ensure the content is well-structured and provides insightful analysis on the topic, with references to the book. "
        # f"Write an assignment based on the following details:\n"
        # f"Topic: {data['topic']}\n"
        # f"Description: {data['description']}\n"
        # f"Take a reference from the book: {data['bookName']} by {data['authorName']}\n"
        # f"Please focus on the aspects mentioned in the description and write in an academic style. "
    )
    return prompt

def generate_pdf(content, form_data):
    """Generate a PDF with wrapped text and proper formatting."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="assignment.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2.0, height - 100, form_data['topic'])

    # Book Name and Author
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2.0, height - 150, f"Book: {form_data['bookName']}")
    p.drawCentredString(width / 2.0, height - 180, f"Author: {form_data['authorName']}")

    # Assignment Content with Proper Word Wrapping
    p.setFont("Helvetica", 12)
    text = p.beginText(50, height - 220)
    text.setTextOrigin(50, height - 220)
    text.setWordSpace(0.5)  # Adjusts spacing for better layout

    # Wrap text to avoid overflow
    for line in content.split('\n'):
        wrapped_lines = [line[i:i+90] for i in range(0, len(line), 90)]  # Set a max line length (adjustable)
        for wrapped_line in wrapped_lines:
            text.textLine(wrapped_line)
    
    p.drawText(text)

    p.showPage()
    p.save()

    return response

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_pdf_view(request):
    """View to generate PDF based on form data."""
    if request.method == 'POST':
        form_data = json.loads(request.body)

        print("Passed to verify the book.")
        # Step 1: Verify the book
        if not verify_book(form_data['bookName'], form_data['authorName']):
            return JsonResponse({'error': 'Book not found'}, status=400)
        print("Book is verified")

        # Step 2: Generate the refined prompt
        prompt = generate_prompt(form_data)
        print("Prompt generated")

        # Step 3: Generate content using the text generator
        response = text_generator(prompt, max_length=500, num_return_sequences=1, truncation=True)
        generated_content = response[0]['generated_text']
        print("Content generated")

        # Step 4: Generate the PDF
        pdf_response = generate_pdf(generated_content, form_data)
        print("PDF generated")
        return pdf_response

    return JsonResponse({'error': 'Invalid request method'}, status=405)





# import json
# import requests
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from django.http import HttpResponse, JsonResponse
# from django.conf import settings
# from transformers import pipeline

# # Load text-generation pipeline (GPT-2 in this case)
# text_generator = pipeline('text-generation', model='gpt2')

# def verify_book(book_name, author_name):
#     """Verify if the book exists using Google Books API."""
#     google_books_url = f'https://www.googleapis.com/books/v1/volumes?q={book_name}+inauthor:{author_name}&key={settings.GOOGLE_BOOKS_API_KEY}'
#     response = requests.get(google_books_url)
#     result = response.json()
#     return 'items' in result and len(result['items']) > 0

# def generate_prompt(data):
#     """Generate a refined prompt for text generation."""
#     prompt = (
#         f"Topic: {data['topic']}\n"
#         f"Book: {data['bookName']} by {data['authorName']}\n"
#         f"Category: {data['category']}\n"
#         f"Description: {data['description']}\n"
#         f"Please focus on the aspects mentioned in the description and write in an academic style."
#     )
#     return prompt

# def extract_generated_content(response):
#     """Extract the generated content, excluding the prompt."""
#     # GPT-generated text sometimes includes the prompt. We'll slice it out by splitting
#     # based on the generated prompt and removing any content before the first actual sentence
#     generated_text = response[0]['generated_text']
#     # Assuming that the response might repeat parts of the prompt, we filter that out
#     first_sentence = generated_text.split('\n', 1)[-1]  # Take the actual generated content
#     return first_sentence.strip()

# def generate_pdf(content, form_data):
#     """Generate a PDF with wrapped text and proper formatting."""
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="assignment.pdf"'

#     p = canvas.Canvas(response, pagesize=A4)
#     width, height = A4

#     # Title
#     p.setFont("Helvetica-Bold", 24)
#     p.drawCentredString(width / 2.0, height - 100, form_data['topic'])

#     # Book Name and Author
#     p.setFont("Helvetica", 14)
#     p.drawCentredString(width / 2.0, height - 150, f"Book: {form_data['bookName']}")
#     p.drawCentredString(width / 2.0, height - 180, f"Author: {form_data['authorName']}")

#     # Assignment Content with Proper Word Wrapping
#     p.setFont("Helvetica", 12)
#     text = p.beginText(50, height - 220)
#     text.setTextOrigin(50, height - 220)
#     text.setWordSpace(0.5)  # Adjusts spacing for better layout

#     # Wrap text to avoid overflow
#     for line in content.split('\n'):
#         wrapped_lines = [line[i:i+90] for i in range(0, len(line), 90)]  # Set a max line length (adjustable)
#         for wrapped_line in wrapped_lines:
#             text.textLine(wrapped_line)
    
#     p.drawText(text)

#     p.showPage()
#     p.save()

#     return response

# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def generate_pdf_view(request):
#     """View to generate PDF based on form data."""
#     if request.method == 'POST':
#         form_data = json.loads(request.body)

#         # Step 1: Verify the book
#         if not verify_book(form_data['bookName'], form_data['authorName']):
#             return JsonResponse({'error': 'Book not found'}, status=400)

#         # Step 2: Generate the refined prompt
#         prompt = generate_prompt(form_data)

#         # Step 3: Generate content using the text generator
#         response = text_generator(prompt, max_length=500, num_return_sequences=1)
#         generated_content = extract_generated_content(response)

#         # Step 4: Generate the PDF
#         pdf_response = generate_pdf(generated_content, form_data)
#         return pdf_response

#     return JsonResponse({'error': 'Invalid request method'}, status=405)
