import pandas
from prettytable import PrettyTable

import matplotlib.pyplot as plt


# DISABILITY CATEGORIES
NO_DISABILITY = 0
ONLY_DEAF = 1
DEAF_PLUS = 2
OTHER_DISABILITY = 3
NO_DISCLOSURE = 4
DISABILITY_CATEGORIES = {NO_DISABILITY:"No disability", ONLY_DEAF:"Deaf", DEAF_PLUS:"Deaf+",
                         OTHER_DISABILITY:"Other disabilities", NO_DISCLOSURE:"No disabilities disclosed"}
DISABILITY_COLORS = {NO_DISABILITY:"sandybrown", ONLY_DEAF:"darksalmon", DEAF_PLUS:"indianred",
                         OTHER_DISABILITY:"firebrick", NO_DISCLOSURE:"maroon"}

# SUPPORT SERVICES CATEGORIES
SUPPORT_SERVICES = "What support services or technology do you use as part of your education?"
CI = "Cochlear implant"
CA = "Captioning"
HA= "Hearing aids"
SLI = "Sign language interpreters"
VA = "Visual aids"
SUPPORT_SERVICES_CATEGORIES = { CA: "Captioning", CI: "Cochlear implant", HA: "Hearing aids",SLI: "Sign language interpreters",
                               VA:"Visual aids"}
SUPPORT_SERVICES_COLORS = { CA: "lightsteelblue", CI: "darkslategray", HA: "steelblue",SLI: "royalblue",
                               VA:"blue"}


# categories for scored questions
CLASSES_REQUESTS = "How often have you been able to successfully request support services you need for classes?"
MEETINGS_REQUESTS = "How often have you been able to successfully request support services you need for meetings?"
ONLINE_TESTS = "How is your experience with taking quizzes and tests online?"
SPEECH_TO_TEXT = "What is your take on speech-to-text services available to you?"
ONLINE_SATISFACTION = "How satisfied are you with your online learning experience?"
SCORED_QUESTIONS = [CLASSES_REQUESTS, MEETINGS_REQUESTS, ONLINE_TESTS, SPEECH_TO_TEXT, ONLINE_SATISFACTION]


def code_disability_categories(responses):
    # NO Disability
    # D/deaf alone
    # D/deaf+
    # other disability
    # prefer not to disclose
    responses["Disability"].replace("None", NO_DISABILITY, inplace=True)
    responses["Disability"].replace("D/deaf", ONLY_DEAF, inplace=True)
    responses["Disability"].replace("Hard of Hearing", ONLY_DEAF, inplace=True)
    responses["Disability"].replace(r'^.*deaf.*$', DEAF_PLUS, regex=True, inplace=True)
    responses["Disability"].replace("Prefer not to disclose", NO_DISCLOSURE, inplace=True)
    responses["Disability"].replace(r'\w', OTHER_DISABILITY, regex=True, inplace=True)


def code_support_services_categories(responses):
    for support_service in SUPPORT_SERVICES_CATEGORIES:
        responses[support_service] = responses[SUPPORT_SERVICES].str.contains(support_service)


def graph_responses(score_by_questions, question_labels_dictionary, a1_header, colors_for_graph):
    for question in score_by_questions:
        plt.figure(figsize=[10,5])

        plt.ylabel(a1_header)
        plt.xlabel("Average Rating by Participant")
        plt.xlim(0,5.5)
        plt.xticks([n/2 for n in range(11)])
        for category in score_by_questions[question]:
            try:
                bar_plot = plt.barh(category, score_by_questions[question][category], color=colors_for_graph[category])
            except KeyError:
                bar_plot = plt.barh(category, score_by_questions[question][category], color='royalblue')

        for i, v in enumerate(score_by_questions[question].values()):
            print(v)
            plt.text(v+0.2, i, str(round(v, 2)), color='midnightblue', va="center")
        plt.title(question, wrap=True)
        plt.tight_layout()

        plt.savefig(a1_header + question_labels_dictionary[question], bbtightbox=True,dpi=100)
        plt.clf()


def output_subjective_score(table_title, a1_header, category_values_dictionary, responses, column_header,
                            bar_graph_colors,
                            strict_search=True):
    print(table_title)
    question_labels = ["Q%s" % (n+1) for n in range(len(SCORED_QUESTIONS))]
    question_labels_dictionary = dict(zip(SCORED_QUESTIONS, question_labels))
    header_args = [a1_header, "No. Participants", "Q1", "Q2", "Q3", "Q4", "Q5"]

    score_table = PrettyTable(header_args)
    score_by_questions = {question:{} for question in SCORED_QUESTIONS}

    print("LaTeX Output:")

    print("\\hline \n" + " & ".join(header_args) + " & \\\\ \\hline")

    for category in category_values_dictionary:
        category_full_name = category_values_dictionary[category]

        if strict_search:
            category_matching_selection = responses.loc[responses[column_header] == category]

        else:
            category_matching_selection = responses.loc[responses[column_header].str.contains(category)]

        category_matching_selection.to_csv(category_full_name + "-responses.csv")
        row_values = [category_full_name, str(len(category_matching_selection))]
        for question in SCORED_QUESTIONS:
            average_score_for_question = category_matching_selection[question].mean()
            row_values.append("{:.2f}".format(average_score_for_question))
            score_by_questions[question][category_full_name] = average_score_for_question
        score_table.add_row(row_values)
        print(" & ".join(row_values)+ " \\\\")
    print("\\hline")
    print(score_table)




    colors_for_graph = dict(zip(category_values_dictionary.values(), bar_graph_colors))
    #graph_responses(score_by_questions, question_labels_dictionary, a1_header, colors_for_graph)




def get_average_subjective_scores(responses):
    print("Latex output:")
    item = "\\item"
    for question in SCORED_QUESTIONS:
        print("\t%s %s \\textbf{[Q%d]}" % (item, question,SCORED_QUESTIONS.index(question)+1))

    print()

    output_subjective_score("Average participant score by disability", "Disability", DISABILITY_CATEGORIES, responses,  "Disability",
                            DISABILITY_COLORS.values()
                           )


    output_subjective_score("Average participant score by support service category", "Support service",
                            SUPPORT_SERVICES_CATEGORIES, responses,SUPPORT_SERVICES, SUPPORT_SERVICES_COLORS.values(),
                             strict_search=False)
    print()



def main():
    responses = pandas.read_csv("responses.csv")
    responses = responses.drop(columns=["Timestamp"])
    code_disability_categories(responses)
    code_support_services_categories(responses)
    get_average_subjective_scores(responses)
    #    print(responses[column].value_counts())


if __name__ == '__main__':
    main()