with open('./german_vocab.txt', encoding='utf-8') as file:
  lines = [line for line in file]
  german_terms = [line.split('-')[0].strip() for line in lines]
  english_terms = [line.split('-')[1].strip() for line in lines]
  terms = zip(german_terms, english_terms)
  quiz_dict = {}
  for german_term, english_term in terms:
    quiz_dict[german_term] = {'answer': english_term}
  print(quiz_dict)