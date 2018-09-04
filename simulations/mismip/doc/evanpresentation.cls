% Basic setup
\ProvidesClass{evanpresentation}

\LoadClass[serif,10pt]{beamer}
\usecolortheme[named=black]{structure} % theme color is now black

\mode<presentation> { \setbeamercovered{transparent} }
\setbeamertemplate{navigation symbols}{}
\makeatletter
\def\beamerorig@set@color{%
  \pdfliteral{\current@color}%
    \aftergroup\reset@color
}
\def\beamerorig@reset@color{\pdfliteral{\current@color}}
\makeatother

\setbeamertemplate{theorems}[ams style]

%\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

%[style=verbose]
\usepackage{makeidx}
\usepackage{import}
\usepackage{bigints}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{mathtools}
\usepackage{amsmath,amsthm,amssymb,amscd}
\usepackage{graphicx}
\usepackage{float}
\usepackage[caption=false]{subfig}
\usepackage{multicol}
\usepackage{tabularx}
\usepackage[format=plain,
            labelfont={bf},
            textfont=it]{caption}
\usepackage[mathscr,mathcal]{euscript}
\usepackage{stmaryrd}
%\usepackage{fouriernc}
%\usepackage{igsupmath}
\usepackage{amsbsy}
\usepackage{amssymb}
\usepackage{bm}
\usepackage{xspace}
\usepackage[scaled=0.90]{beramono}
\usepackage[10pt]{moresize}
\usepackage{makecell}
\usepackage{cancel}
\usepackage[absolute,overlay]{textpos}
\usepackage{ragged2e}
\usepackage{tikz}
\usepackage[nameinlink, capitalize, noabbrev]{cleveref}
\crefformat{equation}{(#2#1#3)}
\crefrangeformat{equation}{(#3#1#4)--(#5#2#6)}
\crefmultiformat{equation}{(#2#1#3)}%
{ and~(#2#1#3)}{, (#2#1#3)}{ and~(#2#1#3)}

\usepackage{ragged2e}
\usepackage{etoolbox}
\apptocmd{\frame}{}{\justifying}{} % Allow optional arguments after frame.

% url links :
\usepackage{hyperref}

\hypersetup{
  final,
  colorlinks,
  linkcolor=black,%{red!80!black},
  citecolor=black,%{red!80!black},
  urlcolor={blue!60!red}
}

% right cases :
%\newenvironment{rcases}
%  {\left.\begin{aligned}}
%  {\end{aligned}\right\rbrace}

% fonts :
\DeclareMathAlphabet{\mathcal}{OMS}{cmsy}{m}{n}   % or txsy
\SetMathAlphabet{\mathcal}{bold}{OMS}{cmsy}{b}{n} % or txsy
\DeclareMathAlphabet{\pazocal}{OMS}{zplm}{m}{n}

\newtheoremstyle{remark}%      % Name
  {}%                          % Space above
  {}%                          % Space below
  {}%                          % Body font
  {}%                          % Indent amount
  {\bfseries}%                 % Theorem head font
  {.}%                         % Punctuation after theorem head
  { }%                         % Space after theorem head, ' ', or \newline
  {}%                          % Theorem head spec (can be left empty, meaning `normal')

\newtheoremstyle{definition}%  % Name
  {}%                          % Space above
  {}%                          % Space below
  {}%                          % Body font
  {}%                          % Indent amount
  {\bfseries}%                 % Theorem head font
  {.}%                         % Punctuation after theorem head
  { }%                         % Space after theorem head, ' ', or \newline
  {}%                          % Theorem head spec (can be left empty, meaning `normal')

\newtheorem{proposition}{Proposition}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

\makeatletter
\newenvironment<>{proofs}[1][\proofname]{%
    \par
    \def\insertproofname{#1\@addpunct{.}}%
    \usebeamertemplate{proof begin}#2}
  {\usebeamertemplate{proof end}}
\makeatother

\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\bigo}{\mathcal{O}}
\newcommand{\G}{\mathcal{G}}
\newcommand{\V}{\mathcal{V}}
\newcommand{\E}{\mathcal{E}}
\newcommand{\K}{\mathcal{K}}
\newcommand{\Hu}{\mathcal{H}}
\newcommand{\Lu}{\mathcal{L}}
\newcommand{\T}{^\intercal}
\newcommand{\var}{\mathrm{Var}}
\newcommand{\mean}{\mathrm{mean}}
\newcommand{\Ex}{\mathrm{E}}
\newcommand{\tr}{\mathrm{tr}}
\newcommand{\diag}{\mathrm{diag}}
\newcommand{\ones}{\mathrm{ones}}
\newcommand{\mat}{\mathbf}
\newcommand{\CSLVR}{\href{http://cslvr.readthedocs.io/en/latest/}{CSLVR}\xspace}
\newcommand{\fenicsMpm}{\href{http://fenics-mpm.readthedocs.io/en/latest/}{\texttt{fenics\_mpm}}\xspace}

% some commands for sub- and super-scripts :
\newcommand{\fint}{\rankone{f}^{\mathrm{int}}}
\newcommand{\fext}{\rankone{f}^{\mathrm{ext}}}
\newcommand{\nthd}{N_{\mathrm{thd}}}
\newcommand{\p}{\mathrm{p}}
\newcommand{\pbas}{\varphi}
\newcommand{\ebas}{\phi}
\newcommand{\extrap}{\widetilde}
\newcommand{\melt}{\mathrm{m}}
\newcommand{\normal}{\rankone{\hat{n}}}

%===============================================================================
% variable subscripts :
\newcommand{\ice}{\mathrm{i}} 
\newcommand{\water}{\mathrm{w}}
\newcommand{\air}{\mathrm{a}}
\newcommand{\liquid}{\ell}
\newcommand{\solid}{\mathrm{s}}
\newcommand{\vapor}{\mathrm{v}}
\newcommand{\rock}{\mathrm{r}}
\newcommand{\seawater}{\mathrm{sw}}
\newcommand{\sensible}{\mathrm{s}}
\newcommand{\latent}{\mathrm{l}}
\newcommand{\ini}{\mathrm{0}}
\newcommand{\crit}{\mathrm{c}}
\newcommand{\m}{\mathrm{m}}
\newcommand{\e}{\mathrm{e}}
\newcommand{\wat}{\mathrm{W}}
\newcommand{\bed}{\mathrm{B}}
\newcommand{\srf}{\mathrm{S}}
\newcommand{\C}{\mathrm{C}}
\newcommand{\tmp}{\mathrm{T}}
\newcommand{\gnd}{\mathrm{G}}
\newcommand{\ext}{\mathrm{E}}
\newcommand{\lat}{\mathrm{L}}
\newcommand{\FS}{\mathrm{FS}}
\newcommand{\BP}{\mathrm{BP}}
\newcommand{\PS}{\mathrm{PS}}
\newcommand{\RS}{\mathrm{RS}}
\newcommand{\IE}{\mathrm{IE}}
\newcommand{\BV}{\mathrm{BV}}
\newcommand{\AG}{\mathrm{AG}}
\newcommand{\geo}{\mathrm{geo}}
\newcommand{\fric}{\mathrm{fric}}
\newcommand{\ob}{\mathrm{ob}}
\newcommand{\eq}{\mathrm{eq}}
\newcommand{\extern}{\mathrm{ext}}
\newcommand{\intern}{\mathrm{int}}
\newcommand{\stz}{\mathrm{stz}}
\newcommand{\lin}{\mathrm{lin}}
\newcommand{\body}{\mathrm{b}}
\newcommand{\ana}{\mathrm{a}}
\newcommand{\true}{\mathrm{true}}
\newcommand{\fs}{\mathring{F}} 
\newcommand{\smb}{\mathring{S}} 
\newcommand{\bmb}{\mathring{B}} 

% italic characters :
\let\Gamma\varGamma
\let\Omega\varOmega
\let\Sigma\varSigma

% Typesetting macros
\newcommand{\blankpage}{\newpage\hbox{}\thispagestyle{empty}\newpage}
\newcommand{\hairsp}{\hspace{1pt}}
\newcommand{\ie}{\textit{i.\hairsp{}e.}\xspace}
\newcommand{\eg}{\textit{e.\hairsp{}g.}\xspace}
\newcommand{\tab}{\hspace*{2em}}
\newcommand{\emp}[1]{\texttt{#1}}
\newcommand{\etc}{\emph{etc}}
\newcommand{\viceversa}{\emph{vice versa}}
\newcommand{\cf}{\textit{cf.}\xspace}

% Math notation macros
\renewcommand{\d}[1]{\ \mathrm{d}#1}
\newcommand{\diff}[1]{\mathrm{d}#1}

\newcommand{\Hdiv}{H(\mathrm{div})}
\newcommand{\Hcurl}{H(\mathrm{curl})}
\newcommand{\Rset}{\ensuremath{\mathbb{R}}}
\newcommand{\inner}[2]{\langle #1, #2 \rangle}
\newcommand{\renni}[2]{\langle #2, #1 \rangle}
\newcommand{\totder}[3][]{\frac{\mathrm{d}^{#1} #2}{\mathrm{d} #3^{#1} }}
\newcommand{\parder}[3][]{\frac{\partial^{#1} #2}{\partial #3^{#1} }}
\newcommand{\deltat}{\Delta t}
%\newcommand{\bm}[1]{#1}
\newcommand{\brac}[1]{\left( {#1} \right)}
\newcommand{\bracc}[1]{\left\{ {#1} \right\}}
\newcommand{\foralls}{\forall\,}
\newcommand{\mesh}{\mathcal{T}_h}
\newcommand{\Poly}[1]{\mathcal{P}_{#1}}
\newcommand{\CiarletSpace}{\mathcal{V}}
\newcommand{\avg}[1]{\langle {#1} \rangle}
\newcommand{\jump}[1]{\left\llbracket {#1} \right\rrbracket}
\newcommand{\jumpn}[1]{\llbracket {#1} \rrbracket_n}
\newcommand{\cgone}{$\mathrm{cG}(1)$}
\newcommand{\supp}{\mathrm{supp}}
\newcommand{\coefvec}[1]{\bm{#1}}
\newcommand{\rankone}[1]{\underline{#1}}
\newcommand{\ranktwo}[1]{\underline{\underline{#1}}}
\newcommand{\rankfour}[1]{\underline{\underline{\underline{\underline{#1}}}}}
\newcommand{\unit}[1]{\hat{\underline{#1}}}

% Math operatorsg
\DeclareMathOperator{\Div}{div}
\DeclareMathOperator{\Grad}{grad}

% Difficult names
\newcommand{\nedelec}{N\'ed\'elec}
\newcommand{\babuska}{Babu\v{s}ka}

% Misc macros
\newcommand{\apriori}{\emph{a~priori}}
\newcommand{\apost}{\emph{a~posteriori}}

\newcommand{\testspace}{S_0^h \subset \mathcal{H}_{E_0}^1(\Omega)}
\newcommand{\trialspace}{S_E^h \subset \mathcal{H}_E^1(\Omega)}
\newcommand{\ltwospace}{M^h \subset L^2(\Omega)}

\newcommand{\Q}{\mathcal{Q}}
  
\DeclareMathOperator*{\argmin}{argmin}
\DeclareMathOperator*{\argmax}{argmax}
\newcommand*{\argminl}{\argmin\limits}
\newcommand*{\argmaxl}{\argmax\limits}

\newfloat{myalgo}{tbhp}{mya}

\newenvironment{Algorithm}[2][tbh]%
{\begin{myalgo}[#1]
\centering
\begin{minipage}{#2}
\begin{algorithm}[H]}%
{\end{algorithm}
\end{minipage}
\end{myalgo}}

\def\changemargin#1#2{\list{}{\rightmargin#2\leftmargin#1}\item[]}
\let\endchangemargin=\endlist 

\newcommand{\sups}[1]{\ensuremath{^{\textrm{#1}}}}
\newcommand{\subs}[1]{\ensuremath{_{\textrm{#1}}}}

\newcommand{\specialcell}[2][c]
{
  \begin{tabular}[#1]{@{}c@{}}#2\end{tabular}
}

\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

\makeatletter
\newsavebox{\mybox}\newsavebox{\mysim}
\newcommand{\distras}[1]
{
  \savebox{\mybox}{\hbox{\kern3pt$\scriptstyle#1$\kern3pt}}%
  \savebox{\mysim}{\hbox{$\sim$}}%
  \mathbin{\overset{#1}{\kern\z@\resizebox{\wd\mybox}{\ht\mysim}{$\sim$}}}%
}
\makeatother

% aligned matrix negative signs:
\makeatletter
\renewcommand*\env@matrix[1][c]{\hskip -\arraycolsep
  \let\@ifnextchar\new@ifnextchar
  \array{*\c@MaxMatrixCols #1}}
\makeatother

%===============================================================================
% code highlighting :
\usepackage[final]{listings}

% define custom colors :
\usepackage{color}
\definecolor{bg}{rgb}{0.96,0.96,0.85}
\definecolor{deepblue}{rgb}{0,0,0.5}
\definecolor{deepred}{rgb}{0.6,0,0}
\definecolor{deepgreen}{rgb}{0,0.5,0}
\definecolor{purp}{RGB}{128,0,128}
\definecolor{ngrn}{RGB}{153,255,85}

\usepackage{xcolor}
\renewcommand{\lstlistlistingname}{Code Listings}
\renewcommand{\lstlistingname}{Code Listing}

\definecolor{gray}{gray}{0.5}

\colorlet{commentcolour}{cyan!40!black}
\colorlet{stringcolour}{magenta!40!blue}
\colorlet{keywordcolour}{red!90!black}
\colorlet{exceptioncolour}{yellow!50!red}
\colorlet{commandcolour}{blue!60!black}
\colorlet{numpycolour}{green!70!blue!90!black}
\colorlet{digitcolour}{cyan!70!blue!90!black}
\colorlet{literatecolour}{red!90!black}
\colorlet{promptcolour}{green!80!black}
\colorlet{specmethodcolour}{violet}
\colorlet{indendifiercolour}{green!70!white}

\newcommand{\framemargin}{5ex}

\newcommand{\literatecolour}{\textcolor{literatecolour}}
\newcommand{\digitcolour}{\textcolor{digitcolour}}

\newcommand\Small{\fontsize{1.00}{5.0}\selectfont}

\newcommand{\pythonstyle}
{
  \lstset
	{
		  language         = python,
      showtabs         = true,
      tab              = ,
      tabsize          = 2,
	    belowcaptionskip = 1\baselineskip,
      aboveskip        = 1ex,
		  frame            = trbl,
		  showstringspaces = false,
		  basicstyle       = \ttfamily\fontsize{4}{4}\selectfont,
			identifierstyle  = \color{black},
      keywordstyle     = \color{keywordcolour}\bfseries,
      commentstyle     = \color{commentcolour}\slshape,
      stringstyle      = \color{stringcolour},
      backgroundcolor  = \color{black!5},
      emphstyle        = \color{blue}\bfseries,
      emph             = {True, False, None},
      otherkeywords    = {\ , \%, \&, \|},
      morestring       = [s]{"""}{"""},
      morestring       = [s]{'''}{'''},
      breaklines       = true,
      breakatwhitespace= true,
      literate         =*%
        {:}{{\literatecolour:}}{1}%
        {=}{{\literatecolour=}}{1}%
        {-}{{\literatecolour-}}{1}%
        {+}{{\literatecolour+}}{1}%
        {*}{{\literatecolour*}}{1}%
        {/}{{\literatecolour/}}{1}%
        {!}{{\literatecolour!}}{1}%
        %{[}{{\color{black}[}}{1}%
        %{]}{{\color{black}]}}{1}%
        %{(}{{\color{black}(}}{1}%
        %{)}{{\color{black})}}{1}%
        {<}{{\literatecolour<}}{1}%
        {>}{{\literatecolour>}}{1}%
        {>>>}{{\textcolor{promptcolour}{>>>}}}{1}%
  }
}

\newcommand{\cstyle}
{
  \lstset
	{
	    belowcaptionskip = 1\baselineskip,
      aboveskip        = 1ex,
		  frame            = trbl,
		  language         = c,
		  showstringspaces = false,
		  basicstyle       = \ttfamily\fontsize{4}{4}\selectfont,
			identifierstyle  = \color{black},
      keywordstyle     = \color{keywordcolour}\bfseries,
      commentstyle     = \color{commentcolour}\slshape,
      stringstyle      = \color{stringcolour},
      backgroundcolor  = \color{black!5},
      emphstyle        = \color{blue}\bfseries,
      %emph             = {True, False, None},
      %otherkeywords    = {\ , \%, \&, \|},
      %morestring       = [s]{"""}{"""},
      %morestring       = [s]{'''}{'''},
      %literate         =*%
      %  {:}{{\literatecolour:}}{1}%
      %  {=}{{\literatecolour=}}{1}%
      %  {-}{{\literatecolour-}}{1}%
      %  {+}{{\literatecolour+}}{1}%
      %  {*}{{\literatecolour*}}{1}%
      %  {/}{{\literatecolour/}}{1}%
      %  {!}{{\literatecolour!}}{1}%
      %  %{[}{{\color{black}[}}{1}%
      %  %{]}{{\color{black}]}}{1}%
      %  %{(}{{\color{black}(}}{1}%
      %  %{)}{{\color{black})}}{1}%
      %  {<}{{\literatecolour<}}{1}%
      %  {>}{{\literatecolour>}}{1}%
      %  {>>>}{{\textcolor{promptcolour}{>>>}}}{1}%
  }
}

% Python environment
\lstnewenvironment{python}[1][]
{
  \pythonstyle
  \lstset{#1}
}
{}

% Python for external files
\newcommand{\pythonexternal}[2][]
{{
  \pythonstyle
  \lstinputlisting[#1]{#2}
}}

% C for external files
\newcommand{\cexternal}[2][]
{{
  \cstyle
  \lstinputlisting[#1]{#2}
}}

% Python for inline
\newcommand\pythoninline[1]
{{
  \pythonstyle
  \lstinline!#1!
}}

% end code highlighting
%===============================================================================


% border matrix with brackets :
\usepackage{etoolbox}
\let\bbordermatrix\bordermatrix
\patchcmd{\bbordermatrix}{8.75}{4.75}{}{}
\patchcmd{\bbordermatrix}{\left(}{\left[}{}{}
\patchcmd{\bbordermatrix}{\right)}{\right]}{}{}

% end function.tex
%===============================================================================

%\usepackage[backend=biber, style=authoryear, sorting=nyt,natbib]{biblatex}
\usepackage[backend      = bibtex,
            maxbibnames  = 2,
            maxcitenames = 2,
            firstinits   = true,
            style        = authoryear,
            sorting      = nyt,
            natbib]{biblatex}
\DefineBibliographyStrings{english}{%
    andothers = {\em et\addabbrvspace al\adddot}
}
\AtEveryBibitem
{
  \clearfield{issn} % Remove issn
  %\clearfield{doi} % Remove doi
  \clearfield{eprint}

  % Remove url except for @online
  \ifentrytype{online}{}
  {
    \clearfield{url}
  }
}

\newenvironment{reference}[2]
{
  \begin{textblock*}{\textwidth}(#1,#2)
  \flushleft
  \fontsize{.1}{.1}\selectfont \it \color{black} 
}
{
  \end{textblock*}
}

\renewcommand*{\bibfont}{\tiny}

% #1: sorting key, #2: prefix for citation, #3: prefix for bibliography
\DeclareRobustCommand{\VAN}[3]{#2} % set up for citation



