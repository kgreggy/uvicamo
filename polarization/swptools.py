import numpy as np

def get_stokes_from_chunk(cnk,wp_ret = np.pi/2,phs_ofst = 0,verbose = False):
    a0,b0,c0,d0,n0 = 0,0,0,0,0

    wt = np.linspace(0,2*np.pi,len(cnk))
    a0 = np.trapz(cnk,wt)/(2*np.pi)
    n0 = np.trapz(cnk*np.cos(2*wt+phs_ofst),wt)/np.pi
    b0 = np.trapz(cnk*np.sin(2*wt+phs_ofst),wt)/np.pi
    c0 = np.trapz(cnk*np.cos(4*wt+phs_ofst),wt)/np.pi
    d0 = np.trapz(cnk*np.sin(4*wt+phs_ofst),wt)/np.pi

    cd = np.cos(wp_ret)
    sd = np.sin(wp_ret)

    S0 = 2*(a0 - c0*(1+cd)/(1-cd))
    S1 = 4*c0/(1-cd)
    S2 = 4*d0/(1-cd)
    S3 = -2*b0/sd
    
    nrm = S0
    
    if n0 > np.sqrt(S1**2 + S2**2 + S3**2)*1e-3 and verbose:
        print('Warning, large sin(2w) conponent detected. Check alignment!')
    
    return np.array([S0,S1,S2,S3])/nrm

def extract_triggers(trig_dat,thrsh=1,schmidt = 0):
    trigz = np.array([])
    for d in range(len(trig_dat)-1):
        if trig_dat[d+1] - trig_dat[d] > thrsh:
            trigz = np.append(trigz,int(d))
    return trigz.astype(int)

def get_polarization_ellipse(S,n_points = 200,scale_by_dop = True, verbose = False):
    '''
    given a stokes vector, return x,y points for an ellipse
    - n_points: number of points in x,y arrays
    - scale_by_dop: Scale down ellipse for partial polarization
    - verbose: enable logging (currently to terminal)
    '''    
    
    S/=S[0]
    
    DPol = np.sqrt(sum(S[1:]**2))
    for k in range(len(S)):
        if abs(S[k]) > 1:
            if verbose:
                print(f'WARNING: S[{k}] is greater than 100% Clipping to 1.')
            S[k] = S[k]/abs(S[k])

    if scale_by_dop:
        S1 = S[1]/DPol
        S2 = S[2]/DPol
        S3 = S[3]/DPol

    psi = 0.5*np.arctan2(S2,S1)
    chi = 0.5*np.arcsin(S3)
    
    a = 1
    b = np.tan(chi)
    
    ba = b/a
    rot = np.matrix([[np.cos(psi), -1*np.sin(psi)],
                     [np.sin(psi), np.cos(psi)]])
    x1, x2, y1, y2 = [], [], [], []
    
    #create an x array for plotting ellipse y values
    x = np.linspace(-a, a, n_points)

    for x in x:
        #cartesian equation of an ellipse
        Y1 = ba*np.sqrt(a**2-x**2)
        #Y1 reflection about the x-axis
        #rotate the ellipse by psi
        XY1 = np.matrix([[x],
                         [Y1]])
        XY2 = np.matrix([[x],
                         [-Y1]])
        y1.append(float((rot*XY1)[1]))
        x1.append(float((rot*XY1)[0]))
        y2.append(float((rot*XY2)[1]))
        x2.append(float((rot*XY2)[0]))

    #x2,y2 reversed in order so that there is continuity in the ellipse (no line through the middle)
    x = (x1+x2[::-1])
    y = (y1+y2[::-1])

    return np.array(x)*DPol, np.array(y)*DPol