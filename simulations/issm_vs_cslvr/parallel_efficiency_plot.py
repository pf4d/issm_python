from pylab import *

import matplotlib as mpl
#mpl.use('Agg')
mpl.rcParams['font.family']          = 'serif'
mpl.rcParams['legend.fontsize']      = 'medium'
mpl.rcParams['text.usetex']          = True
mpl.rcParams['text.latex.preamble']  = ['\usepackage[mathscr]{euscript}']

x_pos_1M = array([1,       2,      4,      8,      16,     36],
                  dtype='float64')
#y_pos_1M = array([155.0,   96.0,   54.0,   34.0,   21.0,   30.0],
#                  dtype='float64')
y_pos_1M = array([12.3174, 7.1439, 4.1811, 2.4166, 1.7914, 1.7256],
                  dtype='float64')

x_cs_100k = array([1,      2,      4,      8,      16,    36,    72],
               dtype='float64')
y_cs_100k = array([63.577, 35.785, 21.123, 13.653, 9.865, 7.390, 7.090],
               dtype='float64')

x_cs_500k = array([1,       2,       4,      8,       16,     36,     72],
               dtype='float64')
y_cs_500k = array([555.819, 394.893, 215.16, 122.485, 86.880, 67.015, 53.665],
               dtype='float64')

fig  = plt.figure(figsize=(6,3))
ax_l = fig.add_subplot(121)
ax_r = fig.add_subplot(122)

ax_l.plot( x_cs_100k,  y_cs_100k[0] / y_cs_100k,               ls='-',  c='k')
ax_l.plot( x_cs_500k,  y_cs_500k[0] / y_cs_500k,               ls='--', c='k')
ax_l.plot( x_pos_1M,   y_pos_1M[0]  / y_pos_1M,                ls='-',  c='r')
                             
ax_r.plot( x_cs_100k,  y_cs_100k[0] / (y_cs_100k*x_cs_100k),   ls='-',  c='k',
           label=r'$n_v = 100$k')
ax_r.plot( x_cs_500k,  y_cs_500k[0] / (y_cs_500k*x_cs_500k),   ls='--', c='k',
           label=r'$n_v = 500$k')
ax_r.plot( x_pos_1M,   y_pos_1M[0]  / (y_pos_1M*x_pos_1M),     ls='-',  c='r',
           label=r'$n_v = 1$M')

ax_r.set_xlim([0,80])
ax_l.set_xlim([0,80])
ax_r.set_ylim([0,1])
ax_l.set_ylim([0,12])
ax_r.set_xlabel(r'$n$')
ax_l.set_xlabel(r'$n$')
ax_r.set_ylabel(r'$T_0 / \left( nT_n \right)$')
ax_l.set_ylabel(r'$T_0 / T_n$')
ax_r.set_title(r'parallel efficiency')
ax_l.set_title(r'speedup ratio')
ax_r.legend()
ax_r.grid()
ax_l.grid()
plt.tight_layout()
plt.show()
