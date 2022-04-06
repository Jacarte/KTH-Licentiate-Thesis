from itertools import zip_longest
import matplotlib.pyplot as plt
import json
import numpy as np
from scipy.optimize import curve_fit
import scipy.stats as stats
import math
from common import *
import sys
from scipy.stats import uniform

def get_times(jsonfile, func, original, random):
    data = json.loads(open(jsonfile, 'r').read())
    timesOriginal = data[func][original]['times']
    timesmultivariant = data[func][random]['times']

    return timesOriginal, timesmultivariant


from seaborn_qqplot import pplot

# Patch qqplot to receive the axis instead


from scipy import stats
def plot_distributions(qqplots=False, normalize=True, remove_outliers=True):

    # To draw approx curve over the histogram
    DRAW_CURVE_OVER=False
    INPUT = sys.argv[1]
    # Each of the resulting execution time jsons
    payloads = [
                f"{INPUT}/libsodium/bin2base64.result.json",
                f"{INPUT}/libsodium/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json",
                f"{INPUT}/libsodium/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json",
                f"{INPUT}/libsodium/crypto_core_ed25519_scalar_invert.result.json",
                f"{INPUT}/libsodium/crypto_core_ed25519_scalar_random.result.json",
                f"{INPUT}/qrcode/run_qr_str.json",
                f"{INPUT}/qrcode/run_qr.json"
    ]
    # Name of the endpoint entry in the payload file
    function = [
                "bin2base64",
                "crypto_aead_chacha20poly1305_ietf_decrypt_detached",
                "crypto_aead_chacha20poly1305_ietf_encrypt_detached",
                "crypto_core_ed25519_scalar_invert",
                "crypto_core_ed25519_scalar_random",
                "run_qr_str",
                "run_qr"
    ]
    # Name of the original execution times field to look for in the payload
    original = [
                "original"
    ]*7
    # Name of the multivariant execution times field to look for in the payload
    multivariant = [
                    "pureRandom"
    ]*7
    # Titles for the subplot
    titles = [
            "bin2base64",
            "decrypt",
            "encrypt",
            "invert",
            "random",
            "qr_str", # escape for latex is done during the plot, dont do the change here
            "qr_image"
    ]

    # plot order, this willl help to rearrange the subplots in an arbitrary order
    order = [2, 1 ,4, 3, 0, 5, 6]

    # Type of the plot: density to plot density histograms
    tpe = ""

    # Number of intervals, this is used to plot the curve over the histogram, the larger, the smoother, however for debugging reasons it is better to have it low
    intervals = 1000
    args = dict()
    common_args = dict(
        bins="auto"
    )
    if tpe == "density":
        args = dict(
            density=True,
            #histtype="step"
        )

    
    tuples = zip_longest(
        payloads,
        function,
        original,
        multivariant,
        titles
    )


    tuples = [
        (
            t[1], # funcname,
            get_times(t[0], t[1], t[2], t[3]),
            t[-1] # tilte
        ) for t in tuples
    ]


    latexify(fig_width=11, fig_height=8.5, font_size=11, tick_size=10)


    # Change the layout of the plots here by changing the nrows and ncols parameters
    # ncols*nrows >= number of subplots
    fig, axs = plt.subplots(nrows=3, ncols=3, sharex=False,constrained_layout = True)

    # flattening the subplots .... there is probably a better way :)
    axs = list(axs[0]) + list(axs[1]) + list(axs[2])
    # axis triming
    for ax in axs[len(function):]:
        ax.remove()
    for i in range(len(axs)):
        ax = axs[i]
        print(i)


        format_axes(ax, show=['bottom',  'left'], hide=['top', 'right'])
        # use custom order then
        fname, times, title = tuples[order[i]]
        

        #print(times)
        original, mult = times
        scale = 1/1000000 # to convert from nanoseconds to milli
        original = [t*scale for t in original if t != -1]
        mult = [t*scale for t in mult if t != -1]
            
        print(fname)
        #print(" & %d & %d & %d & %d \\\\"%(np.median(original), np.std(original), np.median(mult), np.std(mult)))

        print()
        
        #Set the font size
        fontSizeValue = 15

        #print(original, mult)

        tendency = lambda x: np.median(x)
        r=tendency(mult)/tendency(original)
        print(fname,f"x{r}", tendency(original), tendency(mult), stats.mannwhitneyu(original, mult))
        print(fname,f"x{r}", tendency(original), tendency(mult), stats.ks_2samp(original, mult))


        if not qqplots:
            no, binso, patcho = ax.hist(original, bins="auto", alpha=0.5, color="C0", **args)

            nm, binsm, patchm = ax.hist(mult, bins="auto", color="C1", alpha=0.5, **args)

            # Draw curve over
            if DRAW_CURVE_OVER:
                gaussian_kde_zi = stats.gaussian_kde(original)
                gaussian_kde_zi.covariance_factor = lambda : 0.3
                gaussian_kde_zi._compute_covariance()
                x=np.linspace(min(original), max(original), intervals)
                ax.plot(x, gaussian_kde_zi(x),  linewidth=1, label='kde', color="C0")
                
                gaussian_kde_zz = stats.gaussian_kde(mult)
                gaussian_kde_zz.covariance_factor = lambda : 0.3
                gaussian_kde_zz._compute_covariance()
                x=np.linspace(min(mult), max(mult), intervals)
                ax.plot(x, gaussian_kde_zz(x),  linewidth=1, label='kde', color="C1")


                    # original_curvex, original_curve_y = curve_params(no, binso, patcho)
                    #ax.plot(original_curvex, original_curve_y)
            ax.set_title(title.replace("_", "\_"), fontsize=fontSizeValue)
            if i == len(function) - 1:
                leg = ax.legend([
                        "Original binary",
                        "Multivariant binary"
                    ], bbox_to_anchor = (1.3,0.85), fontsize=fontSizeValue
                )
                leg.set_in_layout(False)
            
            #ax.set_yticks([])
            ax.set_xlabel("Execution time ($m_{123}$)", fontsize=fontSizeValue)
            ax.set_ylabel("Density", fontsize=fontSizeValue)

            # Logarithmic scale for y axis
            print("Log scale")
            ax.set_yscale('log')

            ax.tick_params(axis='x')
            ax.tick_params(axis='y')
            ax.set_yticks([10, 100, 1000])
            plt.savefig(f"times.pdf") # collect this file in the root directory at the left side

        else:
            normorig = stats.zscore(original) if normalize else original
            normmult = stats.zscore(mult) if normalize else mult

            ax.set_title(title.replace("_", "\_"), fontsize=fontSizeValue)


            # Remove outliers
            if remove_outliers:
                def filteroutliers(data):
                    q1o = np.quantile(data, 0.1)
                    q3o = np.quantile(data, 0.9)
                    iqr = q3o - q1o
                    q1o = q1o - 1.5*iqr
                    q3o = q3o + 1.5*iqr
                    data = filter(lambda x: x >= q1o and x <= q3o, data)
                    return list(data)
                normorig = filteroutliers(normorig)
                normmult = filteroutliers(normmult)
            #print(normorig, normmult)
            percs = np.linspace(0,100,100)

            data_uniform = np.random.uniform(min(normmult), max(normmult), 1000)
            data_norm = np.random.normal(min(normmult), max(normmult), 1000)

            qn_a = np.percentile(normorig, percs)
            qn_b = np.percentile(normmult, percs)
            #normal_pc = np.percentile(normal, percs)
            uniform_pc = np.percentile(data_uniform, percs)
            norm_pc = np.percentile(data_norm, percs)
            #ax.plot(normal_pc, qn_a, '-')
            #ax.plot(uniform_pc, qn_b, '-')
            ax.plot(qn_a, qn_b, 'o')
            #ax.plot(uniform_pc, qn_b, '.')
            #ax.plot(norm_pc, qn_b, '.')
            
            #plt.show()

            x = np.linspace(np.min((qn_a.min(),qn_b.min())), np.max((qn_a.max(),qn_b.max())))
            ax.plot(x,x, color="k", ls="--", alpha=0.4)
            
            #ax.plot(data_uniform, qn_b,  ls="--", alpha=0.4)
            #ax.plot(normal, qn_b, ls="--", alpha=0.4)

            if i == len(function) - 1:
                leg = ax.legend([
                        "Normal distribution",
                        "Uniform distribution",
                        "Multivariant binary",
                        "Original binary"
                    ], bbox_to_anchor = (1.3,0.85), fontsize=fontSizeValue
                )
                leg.set_in_layout(False)

            plt.tight_layout()
            plt.savefig(f"../plots/qqplots.pdf") # collect this file in the root directory at the left side

    
    #plt.tight_layout()
    #plt.subplots_adjust(wspace=0.4, hspace=0.4)
    #plt.subplot_tool()
    # plt.show()

plot_distributions(qqplots=True, normalize=True)
#plot_distributions(qqplots=False)