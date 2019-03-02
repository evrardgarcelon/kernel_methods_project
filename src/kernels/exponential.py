from src.kernels.kernel import Kernel, KernelCreate
import numpy as np


class ExponentialKernel(Kernel, metaclass=KernelCreate):
    defaultParameters = {"sigma": 1}

    def kernel(self, x, y):
        return np.exp(-np.linalg.norm(x-y)/(2*self.param.sigma**2))


if __name__ == "__main__":
    from src.data.synthetic import GenClassData
    data = GenClassData(300, 3, nclasses=2)
    kernel = ExponentialKernel(data)

    from src.methods.kpca import KPCA
    kpca = KPCA(kernel)
    proj = kpca.project()

    data.show_pca(proj)