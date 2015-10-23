

import math
import operator


all_links = set()
main_dictionary = {}
page_rank_for_each_doc = {}
each_page_outlink_count = {}
damp_factor = 0.85
final_page_ranks = {}
num_of_links = 0
sink_nodes = []
new_page_ranks = {}

import glob
import json

p_files = glob.glob("sandeep/inlinks/*")
r_files = glob.glob("ravi/inlinks/*")
s_files = glob.glob("sai/inlinks/*")

files = []
files.extend(p_files)
files.extend(r_files)
files.extend(s_files)

with open("sandeep/inlinks/map_dict", "r") as c:
    map_dict = json.load(c)

def construct_dictionary():             # construct the dictionary of inlinks and node from the file
    initial_links = []
    with open("wt2g_inlinks.txt",'r') as f:
        line = f.readline()
        while line:
            links = line.split()
            if links[0] not in each_page_outlink_count:     # dictionary for outlink count
                each_page_outlink_count[links[0]] = 0
            for link in links[1:]:
                 if link not in each_page_outlink_count:
                     each_page_outlink_count[link] = 1
                 else:
                     each_page_outlink_count[link] += 1
            main_dictionary[links[0]] = links[1:]
            initial_links += links
            line = f.readline()
    all_links = set(initial_links)
    return all_links

def initialize(all_links):                  # initialize all the links in doc to 1/N value
    print(len(all_links))
    num_of_links = len(all_links)
    prob_of_each_link = 1.0/num_of_links
    for link in all_links:
        final_page_ranks[link] = prob_of_each_link
    len(final_page_ranks)
    return num_of_links

def calculate_outlink_count():                  # find out sink nodes among all the nodes
    for page in each_page_outlink_count:
        if each_page_outlink_count[page] == 0:
            sink_nodes.append(page)

def calculate_perplexity():             # calculate perplexity for next iteration
    sum = 0
    for link in all_links:
        temp = final_page_ranks[link]
        sum += temp * math.log(temp,2)
    return pow(2,(-1*sum))




def check_iteration_possible(old,new):
    old_floor = math.floor(old)
    new_floor = math.floor(new)
    if old_floor == new_floor:
        return 0
    else:
        return 1

def sort_write_dictionary():            # sort the final values and write them to HD
    final_list = []
    sorted_final_page_ranks = sorted(final_page_ranks.items(), key=operator.itemgetter(1), reverse = True)
    id = 1
    for page in sorted_final_page_ranks:
        final_list.append(str(id) + ' ' +str(page[0]) + ' ' + str(page[1]) + '\n')
        id += 1
    page_count = 0
    with open('merged_ranks_other', 'w+') as f:
        for item in final_list:
            page_count += 1
            if page_count>500: break
            f.write(item)


def calculate_page_rank(num_of_links):         # calculate page-rank of all the pages
    old_perplexity = 0.0
    flag = 1
    count = 0
    check = 0
    while flag:
        count += 1
        print(count)
        sinkPR = 0
        for page in sink_nodes:
            sinkPR += final_page_ranks[page]        # calculate sink nodes page rank
        for page in all_links:
            new_page_ranks[page] = (1-damp_factor)/num_of_links
            new_page_ranks[page] += damp_factor * (sinkPR/num_of_links)
            if page not in main_dictionary:
                continue
            for in_link in main_dictionary[page]:
                new_page_ranks[page] += damp_factor * (final_page_ranks[in_link]/each_page_outlink_count[in_link])
        for link in all_links:
            final_page_ranks[link] = new_page_ranks[link]
        new_perplexity = calculate_perplexity()
        print(new_perplexity)
        flag = check_iteration_possible(old_perplexity,new_perplexity)
        if flag == 0:
            check += 1
            if check == 4:
                flag = 0
            else:
                flag = 1
        else:
            check = 0
        old_perplexity = new_perplexity
    sort_write_dictionary()


if __name__ == '__main__':                       # main function
    all_links = construct_dictionary()
    print("construct")
    num_of_links = initialize(all_links)
    print("initialize")
    calculate_outlink_count()
    print("calculate")
    calculate_page_rank(num_of_links)