# -*- coding: utf-8 -*-
from firstexp.models import Politician, SubmitLog


def create_p_hash(option=0):
    """
    :param option: {model(default):0, local:1}
    :return: dict {"pid":"name"}
    """
    p_hash = {}

    # source from model
    if option == 0:
        p_list = Politician.objects.all()
        for p in p_list:
            p_hash[str(p.pid)] = p.name
    # source from local file
    else:
        for line in open("mod_ansi_unified_assembly_50.txt", "r"):
            line = line.strip()
            ll = line.split("\t")
            p_hash[ll[7].split("/")[-1].split(".")[0]] = ll[0]
    return p_hash


def create_pair_list(p_hash):
    """
    :param p_hash: dict {"pid":"name"}
    :return: set that consists of combination ("pid_x", "pid_y")
    """
    return set([tuple(sorted([x, y])) for x in p_hash.keys() for y in p_hash.keys()])


def create_network_from_logs(pair_list, option=0, piv_w_value=1):
    """
    :param pair_list: set that consists of combination (pid_x, pid_y)
    :param option: {model(default):0, local:1}
    :param piv_w_value: float pivot weight to cut off data
    :return: dict {(pid_x, pid_y): weight}
    """
    p_network = dict([(x, (0, 0)) for x in pair_list])
    p_list = Politician.objects.all()
    p_cnt_hash = dict([(str(p.pid), 0) for p in p_list])
    # source from model
    if option == 0:
        q_hash = {"친하": "green", "안 친하": "red"}
        sl_list = SubmitLog.objects.all()
        for sl in sl_list:
            select_tuple = tuple(sorted(sl.select_list.split(",")))
            shown_tuple = tuple(sorted(sl.shown_list.split(",")))
            q_kind = q_hash[sl.q_kind]

            for se in shown_tuple:
                p_cnt_hash[se] += 1

            if len(select_tuple) == 2:
                (w, c) = p_network[select_tuple]
                if q_kind == "red":
                    p_network[select_tuple] = (w-1, c+1)
                else:
                    p_network[select_tuple] = (w+1, c+1)

        for (p1, p2) in p_network.keys():
            weight = p_network[(p1, p2)][0]
            inter = p_network[(p1, p2)][1]
            union = p_cnt_hash[p1]+p_cnt_hash[p2]-inter

            if inter != 0:
                p_network[(p1, p2)] = weight/union
            else:
                p_network[(p1, p2)] = False

    mini_p_network = {}
    for pair in p_network.keys():
        if p_network[pair] != False:
            mini_p_network[pair] = p_network[pair]

    rp_network = {}
    v_piv_ascend = get_piv(mini_p_network.values(), piv_w_value/2, option="ascend")
    v_piv_descend = get_piv(mini_p_network.values(), piv_w_value/2, option="descend")
    for k, v in mini_p_network.items():
        if v >= v_piv_ascend:
            rp_network[k] = v
        if v <= v_piv_descend:
            rp_network[k] = v
    return rp_network


def create_visjs_network_from_raw(p_network, p_hash, option=0):
    """
    :param p_network: dict {"(pid_x, pid_y)": "weight"}
    :param p_hash: dict {"pid":"p_name"}
    :return: tuple (node_list, edge_list)
    """
    node_list = []
    edge_list = []
    node_color = {"background": "white", "border": "#455a64"}

    for x, y in sorted(p_network, key=p_network.get, reverse=True):
        if p_network[(x, y)] != 0:
            px = str(p_hash[x])
            py = str(p_hash[y])
            weight = p_network[(x, y)]

            # only save node which has edges
            node_x = {}
            node_x["id"] = x
            node_x["label"] = px
            node_x["color"] = node_color
            node_y = {}
            node_y["id"] = y
            node_y["label"] = py
            node_y["color"] = node_color
            if node_x not in node_list:
                node_list.append(node_x)
            if node_y not in node_list:
                node_list.append(node_y)

            edge = {}
            edge["from"] = x
            edge["to"] = y
            if weight > 0:
                # familiar relation: pos weight
                edge["color"] = {"color": "green", "highlight": "green"}
            else:
                # unfaimilar relation: neg weight
                edge["color"] = {"color":"red", "highlight": "red"}
            edge["value"] = abs(weight)
            edge_list.append(edge)

    return (node_list, edge_list)

def create_visjs_with_whole_process(option=0, piv_w_value=0.65):
    p_hash = create_p_hash(option)
    pair_list = create_pair_list(p_hash)
    p_network = create_network_from_logs(pair_list, option, piv_w_value)
    visjs_network = create_visjs_network_from_raw(p_network, p_hash)
    return visjs_network

def create_network_with_whole_process(option=0):
    p_hash = create_p_hash(option)
    pair_list = create_pair_list(p_hash)
    p_network = create_network_from_logs(pair_list, option)
    return p_network

def get_piv(l, c, option="ascend"):
    if option == "ascend":
        sl = list(reversed(sorted([x for x in l])))
    else:
        sl = list(sorted([x for x in l]))
    length = len(l)

    if c != 1:
        pidx = int(c*length)
        return sl[pidx]
    else:
        return sl[-1] - 1


if __name__ == "__main__":
    visjs = create_visjs_with_whole_process(1)
    print(visjs[0])
    print(visjs[1])
