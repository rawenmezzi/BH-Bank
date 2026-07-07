from analyse.analyzer import QuestionAnalyzer

analyzer = QuestionAnalyzer()

question = "Quels clients ont fait des transactions suspectes ce mois-ci ?"

result = analyzer.analyze(question)

print(result)