from pylab import *

import matplotlib as mpl
#mpl.use('Agg')
mpl.rcParams['font.family']          = 'serif'
mpl.rcParams['legend.fontsize']      = 'medium'
mpl.rcParams['text.usetex']          = True
mpl.rcParams['text.latex.preamble']  = ['\usepackage[mathscr]{euscript}']

# dx = 5000 :
x_5000 = array([1,       2,  4,  8,  16, 18, 36, 72], dtype='float64')
y_5000 = array([1*60+43, 56, 35, 24, 21, 20, 17, 17], dtype='float64')

# dx = 2500 :
x_2500 = array([1,       2,       4,       9,       18,      36,     72],
               dtype='float64')
y_2500 = array([7*60+53, 4*60+19, 2*60+33, 1*60+41, 1*60+20, 1*60+9, 59],
               dtype='float64')

# dx = 1000 :
x_1000 = array([1, 2, 4, 8, 16, 36, 72], dtype='float64')
y_1000 = array([60*60 + 3*60 + 14,
                33*60 + 54,
                20*60 + 02,
                13*60 + 48,
                10*60 + 44,
                8*60  + 50,
                7*60  + 27], dtype='float64')

fig  = plt.figure(figsize=(6,3))
ax_l = fig.add_subplot(121)
ax_r = fig.add_subplot(122)

ax_l.plot( x_5000, y_5000[0] / y_5000, ls='-',  c='k')
ax_l.plot( x_2500, y_2500[0] / y_2500, ls='--', c='k')
ax_l.plot( x_1000, y_1000[0] / y_1000, ls=':',  c='k')
                                
ax_r.plot( x_5000, y_5000[0] / (y_5000*x_5000), ls='-',  c='k', label=r'$\Delta x = 5000$')
ax_r.plot( x_2500, y_2500[0] / (y_2500*x_2500), ls='--', c='k', label=r'$\Delta x = 2500$')
ax_r.plot( x_1000, y_1000[0] / (y_1000*x_1000), ls=':',  c='k', label=r'$\Delta x = 1000$')

ax_r.set_xlabel(r'$n$ processors')
ax_l.set_xlabel(r'$n$ processors')
ax_r.set_ylabel(r'$T_0 / \left( nT_n \right)$')
ax_l.set_ylabel(r'$T_0 / T_n$')
ax_r.set_title(r'parallel efficiency')
ax_l.set_title(r'speedup ratio')
ax_r.legend()
ax_r.grid()
ax_l.grid()
plt.tight_layout()
plt.savefig('efficiency.pdf')
plt.show()
