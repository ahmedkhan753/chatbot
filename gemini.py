import google.generativeai as genai

API_KEY = "AIzaSyCviYMhPq10IHqxKmBUQxrPZuff7Ki-9LU"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

print("chat with Gemini type exit")
while True:
    user_input = input("you:")
    if user_input.lower() == "exit":
        break
    response = chat.send_message(user_input)
    print("gemini: " , response.text)