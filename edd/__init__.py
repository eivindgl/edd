import pysam as __pysam
import collections
import read_bam
import score_cutoff
import experiment
from logbook import Logger
import eddlib
log = Logger(__name__)

load_experiment = experiment.Experiment.load_experiment 

def experiment_as_binary_bins(exp, score_function, gap_file, min_ratio,
        normalize=True):
    '''
    converts an experiment to a set of binary (-1, 1) bins
    separated by gaps.
    '''
    df = exp.as_data_frame(normalize=normalize)
    gb = experiment.df_as_genome_bins(df, score_function, gap_file)

    opt_score = score_cutoff.ScoreCutoff.from_chrom_scores(
        gb.chrom_bins).optimize()
    if opt_score.ratio > min_ratio:
        log.warn(('Estimated optimal cutoff gives a too high ratio. (%.2f > %.2f'
                 + 'Consider increasing the bin size') % (opt_score.ratio, min_ratio))
        lim_value = opt_score.get_limit_score(min_ratio)
        log.warn('Using non-optimal %.3f as lim value as it gives a ratio of %.2f.' % (lim_value, min_ratio))
    else:
        lim_value = opt_score.lim_value
    return experiment.genome_bins_as_binary(gb, lim_value), opt_score

def df_as_bins(df, gap_file, drop_gaps_smaller_than):
    '''
    converts a already scored df to an object
    containing a dict of bins per chromosome, separated by gaps.
    '''
    chromd = collections.defaultdict(list)
    for _, x in df.iterrows():
        b = util.bed(x['chrom'], x['start'], x['end'],
                x['score'])
        chromd[b.chrom].append(b)
    return eddlib.GenomeBins.with_gaps(chromd, gap_file, drop_gaps_smaller_than)

def parse_bin_size_as_single_number(s):
    if len(s) > 2 and s[-2:].lower() == 'kb':
        return int(s[:-2]) * 1000
    else:
        return int(s)

