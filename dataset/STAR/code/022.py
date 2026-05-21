import requests

# Mock function to simulate calling the trivia API
def call_trivia_api(question_num):
    # In a real scenario, this function would make an HTTP request to the trivia API.
    # For demonstration, it returns a mock question and answer.
    questions = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "What element does 'O' represent on the periodic table?", "answer": "Oxygen"},
        {"question": "Who wrote 'To Kill a Mockingbird'?", "answer": "Harper Lee"}
    ]
    if question_num < len(questions):
        return questions[question_num]
    else:
        return {"question": "No more questions.", "answer": ""}

def trivia_game():
    try:
        num_questions = int(input("How many questions would you like? "))
    except ValueError:
        print("Please enter a valid number.")
        return
    
    correct_answers = 0
    for i in range(num_questions):
        trivia_data = call_trivia_api(i)
        question = trivia_data.get("question")
        correct_answer = trivia_data.get("answer")
        
        if not question or not correct_answer:
            print("Sorry, we have run out of questions.")
            break
        
        print(f"Question {i+1}: {question}")
        user_answer = input("Your answer: ").strip()
        
        if user_answer.lower() == correct_answer.lower():
            print("Correct! Well done.")
            correct_answers += 1
        else:
            print(f"Incorrect. The right answer is {correct_answer}.")
        
    print(f"Game over. You got {correct_answers} out of {num_questions} correct.")
    
    # Further engagement or end session
    further_action = input("Do you want to play again or do something else? (play again/exit) ").lower()
    if further_action == "play again":
        trivia_game()
    else:
        print("Thank you for playing. Goodbye!")

if __name__ == "__main__":
    trivia_game()