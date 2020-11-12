import pandas
import pandas as pd
from matplotlib import gridspec
from prettytable import PrettyTable

import matplotlib.pyplot as plt
import os
from scipy.stats import mannwhitneyu
import researchpy as rp
from scipy.stats import ttest_ind, chi2_contingency, chi2, f_oneway, kruskal
import statistics

DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))


# DISABILITY CATEGORIES
NO_DISABILITY = 0
ONLY_DEAF = 1
DEAF_PLUS = 2
OTHER_DISABILITY = 3
NO_DISCLOSURE = 4
HEARING = 5
DEAF = 6
DISABILITY_CATEGORIES = {NO_DISABILITY:"No disability", ONLY_DEAF:"Deaf", DEAF_PLUS:"Deaf+",
                         OTHER_DISABILITY:"Other disabilities", NO_DISCLOSURE:"No disabilities disclosed",
                         HEARING:"Hearing", DEAF:"D/deaf/HH"}

# SUPPORT SERVICES CATEGORIES
SUPPORT_SERVICES = 'What support services or technology do you use for class?'
CI = "Cochlear implant"
CA = "Captioning"
HA= "Hearing aids"
SLI = "Sign language interpreters"
VA = "Visual aids"
NONE = "None"
SUPPORT_SERVICES_CATEGORIES = { CA: "Captioning", CI: "Cochlear implant", HA: "Hearing aids",SLI: "Sign language interpreters",
                               VA:"Visual aids", NONE:"None"}


# categories for scored questions
CLASS_RELEVANCE = 'My classes are relevant to my chosen field of study.'
CLASS_STRUCTURE = 'In general, my classes are..'
UNDERSTANDING_DUE_DATES = 'I know when assignments are due.'
UNDERSTANDING_CONTENT = 'Overall, I understand the content being taught in my classes.'
LECTURE_FOCUS = 'I am able to focus during lectures.'
COMMUNITY = 'I feel connected to my college community.'
GROUP_WORK = 'Overall, communication and distribution of tasks for group assignments is..'

SCORED_QUESTIONS = [CLASS_RELEVANCE, CLASS_STRUCTURE, UNDERSTANDING_DUE_DATES, UNDERSTANDING_CONTENT, LECTURE_FOCUS,
                    COMMUNITY, GROUP_WORK]


def code_disability_categories(responses):
    # NO Disability
    # D/deaf alone
    # D/deaf+
    # other disability
    # prefer not to disclose
    responses["Disability"].replace("None", NO_DISABILITY, inplace=True)
    responses["Disability"].replace("D/deaf", ONLY_DEAF, inplace=True)

    responses["Disability"].replace("Hard of hearing", ONLY_DEAF, inplace=True)
    responses["Disability"].replace(r'^.*deaf.*$', DEAF_PLUS, regex=True, inplace=True)

    responses["Disability"].replace("Prefer not to disclose", NO_DISCLOSURE, inplace=True)
    responses["Disability"].replace(r'\w', OTHER_DISABILITY, regex=True, inplace=True)


def code_hearing_status(responses):
    responses["Disability"].replace("deaf", DEAF, regex=True, inplace=True)
    responses["Disability"].replace("Hard of hearing", DEAF, inplace=True)
    responses["Disability"].replace("Prefer not to disclose", NO_DISCLOSURE, inplace=True)

    responses["Disability"].replace('None', HEARING, regex=True, inplace=True)
    responses["Disability"].fillna(HEARING, inplace=True)

    responses["Disability"].replace(r'\w', HEARING, regex=True, inplace=True)
    responses["Disability Labels"] = responses["Disability"].copy()

    #TODO fix
    responses["Disability Labels"].replace(HEARING, DISABILITY_CATEGORIES[HEARING], inplace=True)
    responses["Disability Labels"].replace(DEAF, DISABILITY_CATEGORIES[DEAF], inplace=True)



def code_support_services_categories(responses):
    for support_service in SUPPORT_SERVICES_CATEGORIES:
        responses[support_service] = responses[SUPPORT_SERVICES].str.contains(support_service)


def code_student_categories(responses):
    responses.replace(to_replace="Yes, undergraduate.", value="undergrad", inplace=True)
    responses.replace(to_replace="Yes, graduate.", value="grad", inplace=True)
    responses.replace(to_replace="Yes,  high school.", value="hs", inplace=True)


def categorize_response_values(responses):
    # code_disability_categories(responses)
    code_hearing_status(responses)
    code_student_categories(responses)


def compute_mann_whitney_by_question(responses):
    hearing_responses = responses.loc[responses["Disability"] == HEARING]
    deaf_responses = responses.loc[responses["Disability"] == DEAF]
    print("Comparing Deaf and hearing responses to the A3 survey....")
    print("N=%d Deaf, M=%d Hearing " % (len(deaf_responses), len(hearing_responses)))

    with open('likert-chart.tex', 'w')as likert_chart_out:
        likert_chart_out.write("\\begin{table*}[t]\n \t\\centering \n")
        likert_chart_out.write("\t\\begin{tabular}{| c | l | c  c  c  c c | }\n")

        likert_chart_out.write("\t\\hline \t\t Question & Group & $N$ & Median Rank $\Delta $&"
                               "Mann-Whitney U & $p$-value &$r$-value \\\\ \\hline  \n")
        for pre_covid_question in SCORED_QUESTIONS:
            question_label = SCORED_QUESTIONS.index(pre_covid_question) + 1
            print("Q%d: %s" % (question_label, pre_covid_question))
            post_covid_question = pre_covid_question + ".1"

            hearing_pre_covid = hearing_responses[pre_covid_question]
            hearing_post_covid = hearing_responses[post_covid_question]
            deaf_pre_covid = deaf_responses[pre_covid_question]
            deaf_post_covid = deaf_responses[post_covid_question]

            hearing_responses_change = hearing_post_covid - hearing_pre_covid
            deaf_responses_change = deaf_post_covid - deaf_pre_covid
            hearing_responses_change_list = list(hearing_responses_change)
            deaf_responses_change_list = list(deaf_responses_change)

            mann_whitney_u, pvalue = mannwhitneyu(hearing_responses_change_list, deaf_responses_change_list)
            ttstat, ttpvalue = ttest_ind(hearing_responses_change_list, deaf_responses_change_list)

            deaf_r_value = mann_whitney_u/(len(deaf_responses_change_list)**.5)
            hearing_r_value = mann_whitney_u/(len(hearing_responses_change_list)**.5)
            likert_chart_out.write("\t\t\\multirow{2}{*}{Q%d} &  Deaf & %d & %d &"
                                   "%.2f & %.3f & %.3f  \\\\  \n" % (question_label, len(deaf_responses_change_list),
                                                                    statistics.median(deaf_responses_change_list),
                                                                    mann_whitney_u, pvalue, deaf_r_value))
            likert_chart_out.write("\t\t & Hearing & %d & %d "
                                   "&- & - & %.3f \\\\ \\hline  \n" % (len(hearing_responses_change_list),
                                                                        statistics.median(hearing_responses_change_list),
                                                                        hearing_r_value))
            # print(f_oneway(hearing_responses_change_list, deaf_responses_change_list))


        likert_chart_out.write("\t\\end{tabular}")
        likert_chart_out.write("\\end{table*}")


def plot_by_groups(responses):
    # two different chart categories: pre-covid and post-covid. bars= deaf and hearing; 1 per question
    # x axis: n in [1,5]
    # y axis: score range
    widths = [.5,.5]
    heights=[2,2,2,2,2,2,2]
    figure = plt.figure(figsize=(5,10), constrained_layout=True)

    grid_spec = figure.add_gridspec(nrows=7, ncols=2,  figure=figure)
    handles, labels = [], []
    responses = responses.loc[responses["Disability"] != NO_DISCLOSURE]

    for question in SCORED_QUESTIONS:
        question_index = SCORED_QUESTIONS.index(question)

        pre_covid_responses = responses.groupby(['Disability Labels', question]).size().unstack(fill_value=0).transpose()

        post_covid_question = question + ".1"
        post_covid_responses = responses.groupby(['Disability Labels', post_covid_question]).size().unstack(fill_value=0).transpose()

        pre_covid_responses.index.name = None
        post_covid_responses.index.name = None

        # add subplot for the pre and post covid graphs, respectively
        pre_covid_graph = figure.add_subplot(grid_spec[question_index, 0])
        post_covid_graph = figure.add_subplot(grid_spec[question_index, 1])

        handles, labels = post_covid_graph.get_legend_handles_labels()
        pre_covid_responses.plot.bar(rot=0, width=1, ylabel=("Q%d"% (question_index+1)), legend=False, sharex=True, sharey=True, figsize=(3,10),
                                     ax=pre_covid_graph)

        if question_index==0:
            post_covid_responses.plot.bar(rot=0, width=1, sharey=True, figsize=(5,10),
                                          ax=post_covid_graph)
        else:
            post_covid_responses.plot.bar(rot=0, width=1, legend=False, sharey=True, figsize=(5,10),
                                          ax=post_covid_graph)
        figure.legend(handles, labels, loc='lower right')

    xlims = (0,5)
    ylims= (0,15)
    grid_spec[0,1].legend = True
    for ax in figure.get_axes():
        ax.label_outer()
    plt.setp(figure.axes, xlim=xlims, ylim=ylims)


    plt.tight_layout()
    grid_spec.tight_layout(figure)
    plt.show()
    plt.close('all')



def main():
    responses = pandas.read_csv("a3-responses.csv")
    responses = responses.drop(columns=["Timestamp"])
    categorize_response_values(responses)
    compute_mann_whitney_by_question(responses)
    plot_by_groups(responses)


if __name__ == '__main__':
    main()