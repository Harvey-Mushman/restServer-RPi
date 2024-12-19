import numpy as np # for math

class PressureConverter():
    """ converts voltage from a presure sensor to pressure"""

    def __init__(
        self,
        # P = [90, 80, 75, 70, 60, 50, 40, 30, 20, 10, 0],
        # V = [3.126, 2.946, 2.774, 2.627, 2.311, 1.996, 1.661, 1.328, 1.045, 0.74, 0.407],
        # 12/8/2024 jim after installing sensor in water, the readings below were taked from the actural primary water loop
        P = [12.5, 18.75, 25, 37.5, 50, 62.5],
        V = [1.37, 1.48, 1.714, 2.19, 2.531, 2.97]
    ):
        """
        Args:
            P: pressure
            V: voltage
        """

        self.P = np.array(P)
        self.V = np.array(V)
        self.calibrate()

    def __call__(self, V):
        return self.A * V + self.B

    def calibrate(self):
        V = self.V
        P = self.P
        M = np.vstack((
            V,
            np.ones_like(V),
        )).T
        AB = np.linalg.lstsq(M, P, rcond=None)[0]
        self.A, self.B = AB



def main():
    import matplotlib.pyplot as plt # for plotting

    pressure_converter = PressureConverter()

    print("A_ = %e\nB_ = %e"%(
        pressure_converter.A,
        pressure_converter.B))

    # measured data used for calibration
    V_measured = pressure_converter.V
    P_measured = pressure_converter.P

    # fit curve
    V = np.linspace(0,4,20)
    P = pressure_converter(V)

    # plot
    plt.plot(V_measured, P_measured, '.')
    plt.plot(V, P, '-')
    plt.xlabel("voltage")
    plt.ylabel("pressure (psi)")
    plt.legend(["measured data", "fit curve"])
    plt.show()


if __name__ == "__main__":
    main()