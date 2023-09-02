from symbolic_solver.problem.problem import Problem
from symbolic_solver.aux_tools.parser import EquationParser as EqParser
from symbolic_solver.aux_tools.parser import FormalLanguageParser as FLParser
from symbolic_solver.aux_tools.parser import InverseParser as IvParser
from symbolic_solver.core.engine import EquationKiller as EqKiller
from symbolic_solver.core.engine import GeometryPredicateLogic as GeoLogic
from symbolic_solver.aux_tools.utils import rough_equal
import warnings
import time


class Interactor:

    def __init__(self, predicate_GDL, theorem_GDL):
        """
        Initialize Interactor.
        :param predicate_GDL: predicate GDL.
        :param theorem_GDL: theorem GDL.
        """
        self.predicate_GDL = FLParser.parse_predicate(predicate_GDL)
        self.theorem_GDL = FLParser.parse_theorem(theorem_GDL, self.predicate_GDL)
        self.problem = None

    def load_problem(self, problem_CDL):
        """Load problem through problem_CDL."""
        start_time = time.time()
        self.problem = Problem()
        self.problem.load_problem_by_fl(self.predicate_GDL, FLParser.parse_problem(problem_CDL))  # load problem
        EqKiller.solve_equations(self.problem)  # Solve the equations after initialization
        self.problem.step("init_problem", time.time() - start_time)  # save applied theorem and update step

    def apply_theorem(self, theorem_name, theorem_para=None):
        """
        Apply a theorem and return whether it is successfully applied.
        :param theorem_name: <str>.
        :param theorem_para: tuple of <str>, set None when rough apply theorem.
        :return update: True or False.
        """
        if self.problem is None:
            e_msg = "Problem not loaded. Please run <load_problem> before run <apply_theorem>."
            raise Exception(e_msg)
        if theorem_name not in self.theorem_GDL:
            e_msg = "Theorem {} not defined in current GDL.".format(theorem_name)
            raise Exception(e_msg)
        if theorem_name.endswith("definition"):
            e_msg = "Theorem {} only used for backward reason.".format(theorem_name)
            raise Exception(e_msg)
        if theorem_para is not None and len(theorem_para) != len(self.theorem_GDL[theorem_name]["vars"]):
            e_msg = "Theorem <{}> para length error. Expected {} but got {}.".format(
                theorem_name, len(self.theorem_GDL[theorem_name]["vars"]), theorem_para)
            raise Exception(e_msg)

        if theorem_para is not None:
            update = self.apply_theorem_accurate(theorem_name, theorem_para)  # mode 1, accurate mode
        else:
            update = self.apply_theorem_rough(theorem_name)  # mode 2, rough mode

        if not update:
            w_msg = "Theorem <{},{}> not applied. Please check your theorem_para or prerequisite.".format(
                theorem_name, theorem_para)
            warnings.warn(w_msg)

        return update

    def apply_theorem_accurate(self, theorem_name, theorem_para):
        """
        Apply a theorem in accurate mode and return whether it is successfully applied.
        :param theorem_name: <str>.
        :param theorem_para: tuple of <str>
        :return update: True or False.
        """
        update = False
        start_time = time.time()  # timing

        theorem = IvParser.inverse_parse_logic(  # theorem + para
            theorem_name, theorem_para, self.theorem_GDL[theorem_name]["para_len"])

        letters = {}  # used for vars-letters replacement
        for i in range(len(self.theorem_GDL[theorem_name]["vars"])):
            letters[self.theorem_GDL[theorem_name]["vars"][i]] = theorem_para[i]

        for branch in self.theorem_GDL[theorem_name]["body"]:
            gpl = self.theorem_GDL[theorem_name]["body"][branch]
            premises = []
            passed = True

            for predicate, item in gpl["products"] + gpl["logic_constraints"]:
                oppose = False
                if "~" in predicate:
                    oppose = True
                    predicate = predicate.replace("~", "")
                item = tuple(letters[i] for i in item)
                has_item = self.problem.condition.has(predicate, item)
                if has_item:
                    premises.append(self.problem.condition.get_id_by_predicate_and_item(predicate, item))

                if (not oppose and not has_item) or (oppose and has_item):
                    passed = False
                    break

            if not passed:
                continue

            for equal, item in gpl["algebra_constraints"]:
                oppose = False
                if "~" in equal:
                    oppose = True
                eq = EqParser.get_equation_from_tree(self.problem, item, True, letters)
                solved_eq = False

                result, premise = EqKiller.solve_target(eq, self.problem)
                if result is not None and rough_equal(result, 0):
                    solved_eq = True
                premises += premise

                if (not oppose and not solved_eq) or (oppose and solved_eq):
                    passed = False
                    break

            if not passed:
                continue

            for predicate, item in gpl["conclusions"]:
                if predicate == "Equal":  # algebra conclusion
                    eq = EqParser.get_equation_from_tree(self.problem, item, True, letters)
                    update = self.problem.add("Equation", eq, premises, theorem) or update
                else:  # logic conclusion
                    item = tuple(letters[i] for i in item)
                    update = self.problem.add(predicate, item, premises, theorem) or update

        EqKiller.solve_equations(self.problem)

        self.problem.step(theorem, time.time() - start_time)

        return update

    def apply_theorem_rough(self, theorem_name):
        """
        Apply a theorem in rough mode and return whether it is successfully applied.
        :param theorem_name: <str>.
        :return update: True or False.
        """
        update = False
        start_time = time.time()  # timing

        theorem_list = []
        for branch in self.theorem_GDL[theorem_name]["body"]:
            gpl = self.theorem_GDL[theorem_name]["body"][branch]

            conclusions = GeoLogic.run(gpl, self.problem)  # get gpl reasoned result

            for letters, premise, conclusion in conclusions:
                theorem_para = [letters[i] for i in self.theorem_GDL[theorem_name]["vars"]]
                theorem = IvParser.inverse_parse_logic(  # theorem + para, add in problem
                    theorem_name, theorem_para, self.theorem_GDL[theorem_name]["para_len"])
                theorem_list.append(theorem)

                for predicate, item in conclusion:  # add conclusion
                    update = self.problem.add(predicate, item, premise, theorem) or update

        EqKiller.solve_equations(self.problem)

        self.problem.step(theorem_name, 0)
        if len(theorem_list) > 0:
            timing = (time.time() - start_time) / len(theorem_list)
            for t in theorem_list:
                self.problem.step(t, timing)

        return update
