import numpy as np

class rkf():

    def __init__(self,f, a, b, x0, atol=1e-8, rtol=1e-6, hmax=1e-1, hmin=1e-40):
        self.f=f
        self.a=a
        self.b=b
        self.x0=x0
        self.atol=atol
        self.rtol=rtol
        self.hmax=hmax
        self.hmin=hmin

    def solve(self):

        a2  =   2.500000000000000e-01  #  1/4
        a3  =   3.750000000000000e-01  #  3/8
        a4  =   9.230769230769231e-01  #  12/13
        a5  =   1.000000000000000e+00  #  1
        a6  =   5.000000000000000e-01  #  1/2

        b21 =   2.500000000000000e-01  #  1/4
        b31 =   9.375000000000000e-02  #  3/32
        b32 =   2.812500000000000e-01  #  9/32
        b41 =   8.793809740555303e-01  #  1932/2197
        b42 =  -3.277196176604461e+00  # -7200/2197
        b43 =   3.320892125625853e+00  #  7296/2197
        b51 =   2.032407407407407e+00  #  439/216
        b52 =  -8.000000000000000e+00  # -8
        b53 =   7.173489278752436e+00  #  3680/513
        b54 =  -2.058966861598441e-01  # -845/4104
        b61 =  -2.962962962962963e-01  # -8/27
        b62 =   2.000000000000000e+00  #  2
        b63 =  -1.381676413255361e+00  # -3544/2565
        b64 =   4.529727095516569e-01  #  1859/4104
        b65 =  -2.750000000000000e-01  # -11/40

        r1  =   2.777777777777778e-03  #  1/360
        r3  =  -2.994152046783626e-02  # -128/4275
        r4  =  -2.919989367357789e-02  # -2197/75240
        r5  =   2.000000000000000e-02  #  1/50
        r6  =   3.636363636363636e-02  #  2/55

        c1  =   1.157407407407407e-01  #  25/216
        c3  =   5.489278752436647e-01  #  1408/2565
        c4  =   5.353313840155945e-01  #  2197/4104
        c5  =  -2.000000000000000e-01  # -1/5

        t = float(self.a)
        x = np.array(self.x0, dtype='f8')
        h = float(self.hmax)

        T = np.array( [t] )
        X = np.array( [x] )

        reps = 0

        while t < self.b:
            reps += 1
            #if t + h > self.b:
            #    h = self.b - t
            h = min(h, self.b - t)

            k1 = h * self.f(t, x)
            k2 = h * self.f(t + a2 * h, x + b21 * k1 )
            k3 = h * self.f(t + a3 * h, x + b31 * k1 + b32 * k2)
            k4 = h * self.f(t + a4 * h, x + b41 * k1 + b42 * k2 + b43 * k3)
            k5 = h * self.f(t + a5 * h, x + b51 * k1 + b52 * k2 + b53 * k3 + b54 * k4)
            k6 = h * self.f(t + a6 * h, x + b61 * k1 + b62 * k2 + b63 * k3 + b64 * k4 + b65 * k5)

            r = abs( r1 * k1 + r3 * k3 + r4 * k4 + r5 * k5 + r6 * k6 ) / h
            r = r / (self.atol+self.rtol*(abs(x)+abs(k1)))
            if len( np.shape( r ) ) > 0:
                r = max( r )
            if r <= 1:
                t = t + h
                x = x + c1 * k1 + c3 * k3 + c4 * k4 + c5 * k5
                T = np.append( T, t )
                if x[1]<0.0:
                    x[1] = 0.0
                X = np.append( X, [x], 0 )
                if x[1]<=0.0:
                    break
            if r > 0.0:
                h = h * min( max( 0.94 * ( 1 / r )**0.25, 0.1 ), 4.0 )
            if h > self.hmax:
                h = self.hmax
            elif h < self.hmin or t==t-h:
                raise RuntimeError("Error: Could not converge to the required tolerance.")
                break

        return (T,X)