import attr
import pandas as pd
from dowhy.do_why import CausalModel
import dowhy.datasets as ds
from IPython.display import Image, display
import numpy as np


def add_node(gml, source, target):
    gml = gml + "".join('node[ id "{0}" label "{0}"] edge[ source "{0}" target "{1}"]'.format(source, target))
    return gml


def connect_node(gml, source, edge):
    gml = gml + "".join('edge[ source "{0}" target "{1}"]'.format(source, edge))
    return gml


@attr.s
class DoWhyExample:
    data_old = ds.linear_dataset(beta=10, num_common_causes=5, num_instruments=5, num_samples=10000,
                                 treatment_is_binary=True)

    gml_graph = ('graph[directed 1'
                 'node[ id "TOJ" label "TOJ"]'
                 'node[ id "IntCur" label "IntCur"]'
                 'node[ id "U" label "Unobserved Confounders"]'
                 'edge[source "TOJ" target "IntCur"]'
                 'edge[source "U" target "TOJ"]'
                 'edge[source "U" target "IntCur"]'
                 )

    gml_graph = add_node(gml_graph, "YeshivaAdults", "IntCur")
    gml_graph = add_node(gml_graph, "Sex", "IntCur")
    gml_graph = add_node(gml_graph, "Age", "IntCur")
    gml_graph = connect_node(gml_graph, "Age", "TOJ")
    gml_graph = connect_node(gml_graph, "Age", "YeshivaAdults")
    gml_graph = connect_node(gml_graph, "Sex", "YeshivaAdults")
    gml_graph = connect_node(gml_graph, "TOJ", "YeshivaAdults")
    gml_graph = gml_graph + ']'
    # table
    # ID    Age     Sex     TOJ (Orthodox)? (Treatment?)     Yeshiva?    Intell. Curios? (Outcome)

    data = pd.DataFrame(np.array([[30.0, 1.0, 1.0, 1.0, 0.0], [40.0, 1.0, 0.0, 0.0, 1.0]]),
                        columns=['Age', 'Sex', 'TOJ', 'YeshivaAdults', 'IntCur'])
    #
    t_model = None
    t_identify = None
    t_estimate = None

    def model(self, force_again=False):

        if self.t_model is None or force_again:
            self.t_model = CausalModel(data=self.data, treatment='TOJ', outcome='IntCur', graph=self.gml_graph)
            # CausalModel(data=self.data["df"],
            #                        treatment=self.data["treatment_name"],
            #                        outcome=self.data["outcome_name"],
            #                        graph=self.data["gml_graph"])

        return self.t_model

    def identify(self, force_again=False):
        if self.t_identify is None or force_again:
            if self.t_model is None or force_again:
                self.model(force_again=force_again)
            self.t_identify = self.t_model.identify_effect()
        return self.t_identify

    def estimate(self, method_name="backdoor.propensity_score_matching", force_again=False):
        if self.t_estimate is None or force_again:
            self.t_estimate = self.t_model.estimate_effect(self.identify(force_again), method_name)
        return self.t_estimate

    def refute(self, method_name="random_common_cause", force_again=False):
        return self.model(force_again=force_again).refute_estimate(self.identify(force_again),
                                                                   self.estimate(force_again=force_again),
                                                                   method_name=method_name)


dy = DoWhyExample()
dy.model()
print(dy.estimate())
print(dy.refute())

# dataframe, meta = pyreadstat.read_sav(
#             "e:\\IIT\\Respondent Dataset - 2013 Pew Research Center Survey of US Jews (SPSS) - Version 1.1 - October 1 2014.sav")
# surv_data = pd.DataFrame(dataframe[['sex', 'qe5f', 'qh1cmbrec', 'qh2rec', 'age', 'agecat']])  #  CHDENOM2REC
# print(surv_data.head(20))
