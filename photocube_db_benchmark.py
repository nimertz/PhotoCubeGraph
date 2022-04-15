#!/usr/bin/env python3
"""
This is a benchmarking suite used to compare PostgreSQL and Neo4j photocube queries.

Dependencies:
pip install numpy - for plotting custom barcharts
pip install click - for command line interface
pip install seaborn - for plotting
pip install neo4j - To install Neo4j driver (4.4.0)
pip install psycopg - To install PostgreSQL driver (3.0.11)
"""
__author__ = "Nikolaj Mertz"

import click

import datetime
import random
import logging
import sys

import matplotlib.pyplot as plt
import seaborn as sbn
import numpy as np
import psycopg
from neo4j import GraphDatabase

import Neo4JPhotocube
import PostgresqlPhotocube


def gen_random_id(max_id):
    return random.randint(1, max_id)

def exec_bench_rand_id(name, category, query_method, reps, max_id, result):
    logger.info("Running " + name + " benchmark in " + category + " with " + str(reps) + " reps")
    for _ in range(reps):
        start = datetime.datetime.now()
        query_method(gen_random_id(max_id))
        end = datetime.datetime.now()
        duration = end - start
        result["query"].append(name)
        result["latency"].append(duration.total_seconds() * 1e3)
        result["category"].append(category)
    return result

def random_state_benchmark(reps,result):
    # generate different queries
    type_options = ["S", "H"]
    S_filter_max = max_tagset_id
    H_filter_max = max_node_id
    logger.info("Running state neo4j & postgresql benchmark with " + str(reps) + " reps")
    for i in range(reps):
        numdims = 3
        numtots = 3
        types = []
        filts = []
        for i in range(numdims):
            types.append(type_options[random.randint(0, 1)])
            if types[i] == "S":
                filts.append(gen_random_id(S_filter_max))
            else:
                filts.append(gen_random_id(H_filter_max))

        #print(str(types) + "\n" + str(filts))

        start = datetime.datetime.now()
        neo.query_state(neo.gen_state_query(numdims, numtots, types, filts))
        end = datetime.datetime.now()
        duration = end - start
        neo4j_time = duration.total_seconds() * 1e3
        if neo4j_time > 2000:
            logger.warning("Neo4j time: " + str(round(neo4j_time, 2)) + " ms" +
                  " query: " + str(types) + " " + str(filts))
        result["query"].append("Random state")
        result["latency"].append(neo4j_time)
        result["category"].append("Neo4j")

        start = datetime.datetime.now()
        psql.execute_query(psql.gen_state_query(numdims, numtots, types, filts))
        end = datetime.datetime.now()

        duration = end - start
        psql_time = duration.total_seconds() * 1e3
        if psql_time > 2000:
            logger.warning("PostgreSQL time: " + str(round(psql_time, 2)) + " ms" +
                  " query: " + str(types) + " " + str(filts))
        result["query"].append("Random state")
        result["latency"].append(psql_time)
        result["category"].append("PostgreSQL")

    return result

def neo4j_state_benchmark(name, reps, result):
    # generate different queries
    type_options = ["S", "H"]
    S_filter_max = max_tagset_id
    H_filter_max = max_node_id
    logger.info("Running " + name + " benchmark with " + str(reps) + " reps")
    for i in range(reps):
        numdims = 3
        numtots = 3
        types = []
        filts = []
        for i in range(numdims):
            types.append(type_options[random.randint(0, 1)])
            if types[i] == "S":
                filts.append(gen_random_id(S_filter_max))
            else:
                filts.append(gen_random_id(H_filter_max))

        #print(str(types) + "\n" + str(filts))

        start = datetime.datetime.now()
        neo.query_state(neo.gen_state_query(numdims, numtots, types, filts))
        end = datetime.datetime.now()
        duration = end - start
        time = duration.total_seconds() * 1e3
        if time > 2000:
            print("time: " + str(round(time, 2)) + " ms" +
                  " query: " + str(types) + " " + str(filts))
        if name not in result:
            result[name] = []
        result[name].append(time)
    return result

def postgresql_state_benchmark(name, reps, result):
    # generate different queries
    type_options = ["S", "H"]
    S_filter_max = max_tagset_id
    H_filter_max = max_node_id
    logger.info("Running " + name + " benchmark with " + str(reps) + " reps")
    for i in range(reps):
        numdims = 3
        numtots = 3
        types = []
        filts = []
        for i in range(numdims):
            types.append(type_options[random.randint(0, 1)])
            if types[i] == "S":
                filts.append(gen_random_id(S_filter_max))
            else:
                filts.append(gen_random_id(H_filter_max))

        #print(str(types) + "\n" + str(filts))

        start = datetime.datetime.now()
        psql.execute_query(psql.gen_state_query(numdims, numtots, types, filts))
        end = datetime.datetime.now()

        duration = end - start
        time = duration.total_seconds() * 1e3
        if time > 2000:
            logger.warning("time: " + str(round(time, 2)) + " ms" +
                  " query: " + str(types) + " " + str(filts))
        if name not in result:
            result[name] = []
        result[name].append(time)
    return result

def create_barchart(title, results):
    # seaborn bar plot of results
    sbn.set(style="darkgrid")
    sbn.despine()
    ax = sbn.barplot(x="query", y="latency",hue="category", data=results, log=True,palette="Set2", capsize=.1)
    ax.set(xlabel='Query', ylabel='Mean Latency (ms) - Log scale', title=title)
    show_barchart_values(ax)
    logger.info("Latency barchart created for : " + title)
    return ax

def show_barchart_values(axs, orient="v", space=.01):
    def _single(ax):
        if orient == "v":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 1.7 # change to move text to the right
                _y = p.get_y() + p.get_height() + (p.get_height()*0.01)
                value = '{:.1f}'.format(p.get_height())
                ax.text(_x, _y, value, ha="left")
        elif orient == "h":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(space)
                _y = p.get_y() + p.get_height() - (p.get_height()*0.5)
                value = '{:.1f}'.format(p.get_width())
                ax.text(_x, _y, value, ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _single(ax)
    else:
        _single(axs)

def state_bench(reps,query,name,category,result):
    for i in range(reps):
        start = datetime.datetime.now()
        psql.execute_query(query)
        end = datetime.datetime.now()

        duration = (end - start).total_seconds() * 1e3
        result["query"].append(name)
        result["latency"].append(duration)
        result["category"].append(category)
    return result

def baseline_materialize_index_benchmark(category, reps, result, numdims, numtots, types, filts):
    baselineQuery = psql.gen_state_query(numdims, numtots, types, filts,baseline=True)
    materializedViewQuery = psql.gen_state_query(numdims, numtots, types, filts)

    #drop materialized view indexes
    psql.drop_materialized_indexes()

    state_bench(reps, baselineQuery, "Baseline", category, result)
    state_bench(reps, materializedViewQuery,"Materialized Views", category, result)
    #create materialized view indexes
    psql.create_materialized_indexes()
    state_bench(reps, materializedViewQuery,"Indexed Views", category, result)
    return result

#simple
def simple_state_benchmark(category,reps,result):
    # 2D browsing state with the top level of the
    # entity hierarchy on one axis and location on
    # the other axis
    numdims = 2
    numtots = 2
    types = ["H", "S"]
    filts = [40, 15]

    return baseline_materialize_index_benchmark(category, reps, result, numdims, numtots, types, filts)


def medium_state_benchmark(category,reps,result):
    """ 3D browsing state with the top level of the
    entity hierarchy on the first axis, the
    children of the Dog node on the second axis,
    and timezone on the third axis. """
    numdims = 3
    numtots = 3
    types = ["H", "H", "S"]
    filts = [40, 5, 14]
    
    return baseline_materialize_index_benchmark(category, reps, result, numdims, numtots, types, filts)


def complex_state_benchmark(category,reps,result):
    """ 3D browsing state with the top level of the
    entity hierarchy on the first axis, the
    children of the Dog node on the second axis,
    and location on the third axis. """
    numdims = 3
    numtots = 3
    types = ["H", "H", "S"]
    filts = [40, 5, 15]

    return baseline_materialize_index_benchmark(category, reps, result, numdims, numtots, types, filts)

#Creating and Configuring Logger

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
                    stream = sys.stdout, 
                    format = Log_Format,
                    level=logging.INFO)

logger = logging.getLogger()

max_tag_id = 193189
max_tagset_id = 21
max_hierarchy_id = 3
max_node_id = 8842
max_object_id = 183386

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123"))
neo = Neo4JPhotocube.Neo4jPhotocube(driver)

psql_conn = psycopg.connect(user="photocube", password="123", host="127.0.0.1", port="5432", dbname="photocube")
psql = PostgresqlPhotocube.PostgresqlPhotocube(psql_conn)



@click.group()
def benchmark():
    pass

@benchmark.command("complete")
@click.option("--r", default=10, help="Number of repetitions")
def standard_latency_benchmark(r):
    logger.info("Running standard latency benchmark with " + str(r) + " repetitions")
    results = {'query': [], 'latency': [], 'category': []}

    exec_bench_rand_id("Tag by id", "PostgreSQL", psql.get_tag_by_id, r, max_tag_id, results)
    exec_bench_rand_id("Tag by id", "Neo4j", neo.get_tag_by_id, r, max_tag_id, results)



    exec_bench_rand_id("Tags in tagset", "PostgreSQL", psql.get_tags_in_tagset, r, max_tagset_id, results)
    exec_bench_rand_id("Tags in tagset", "Neo4j", neo.get_tags_in_tagset, r, max_tagset_id, results)

    exec_bench_rand_id("Node tag subtree", "Neo4j", neo.get_node_tag_subtree, r, max_node_id, results)

    random_state_benchmark(r, results)

    title = "Latency of Photocube queries of Neo4j and Postgresql" + "\n" + "Query repetitions: %i " % r
    create_barchart(title, results)
    plt.show()
    neo.close()
    psql.close()

@benchmark.command(name="state")
@click.option("--r", default=10, help="Number of repetitions")
def state_scenarios_and_progression_benchmark(r):
    logger.info("Running state scenarios and progression benchmark with " + str(r) + " repetitions")
    results = {'query': [], 'latency': [], 'category': []}

    simple_state_benchmark("Simple", r,results)
    medium_state_benchmark("Medium",r,results)
    complex_state_benchmark("Complex",r,results)

    title ='Photocube state latency results \n Query repetitions:' + str(r) + ''
    create_barchart(title,results)
    plt.show()
    neo.close()
    psql.close()


if __name__ == '__main__':
    benchmark()



