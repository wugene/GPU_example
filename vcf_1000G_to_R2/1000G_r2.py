
import numpy as np
from r_sq_tf import r_square
from pandas import DataFrame
import argparse



def arg_parse():
    parser = argparse.ArgumentParser(
       description="""Process 1000G vcf to get R-square values.
The first line is used as y.
The rest lines are used as X.
Get R-square values of X and y""")
    parser.add_argument('-i', metavar='in-file',
                    type=argparse.FileType('rt'))
    parser.add_argument('-o', metavar='out-file',
                    type=argparse.FileType('wt'))
    parser.add_argument('-r', metavar='r2-cutoff',
                    type=float, default=0.0)

    try:
        results = parser.parse_args()
        print('Input file:', results.i)
        print('Output file:', results.o)
        print('r2 cutoff:', results.r)
    except IOError as msg:
        parser.error(str(msg))
        exit()

    return results



def vcf1000G_to_r2(v_1000G):

    v_new = DataFrame()
    for col in v_1000G.iloc[:,9:]:
        v_new[str(col)+"L"], v_new[str(col)+"R"] = v_1000G[col].str.split('|', 1).str

    y = v_new[0:1]
    X = v_new[1:]
    r2 = r_square(X, y)

    r2_res = v_1000G.iloc[1:,0:3]
    r2_res.columns = ['chr','pos','id']
    r2_res['r2'] = np.nan_to_num(r2)
    return r2_res


if __name__ == "__main__":
    args = arg_parse()
    infile = args.i
    outfile = args.o
    cutoff = args.r

    v_1000G = DataFrame.from_csv(infile, sep='\t', header=None, index_col=None)
    r2_res = vcf1000G_to_r2(v_1000G)
    r2_res_cut = r2_res.ix[(r2_res['r2']>=cutoff)]
    r2_res_cut.to_csv(outfile, sep='\t', index=False)

