
import sys
import ollama

def main():
    if len(sys.argv) > 1:
        user_message = sys.argv[1]
        response = ollama.chat(model='llama2', messages=[
            {
                'role': 'user',
                'content': user_message,
            },
        ])
        print(response['message']['content'])

if __name__ == "__main__":
    main()
