from cvxopt import matrix, solvers
import numpy as np
from src.methods.KMethod import KMethod, KMethodCreate, klogger

solvers.options['show_progress'] = False

# Solve the QP Problem:
#  minimize    1/2 x^T*P*x + q^T*x
#  subject to  G*x <= h
#              A*x <= b
# solvers.qp(P, q, G, h)


class KSVM(KMethod, metaclass=KMethodCreate):
    """Documentation for KSVM
    Solve the KSVM problem:
        minimize    (1/2)*x^T*K*x - y^T*x
        subject to  0 <= yi*xi <= C
    """
    name = "ksvm"
    defaultParameters = {"C": 1.0, "tol": 10**-4}

    @klogger("Kernel Support Vector Machine")
    def fit(self, K):
        n = self.n
        y = self.labels
        C = self.param.C

        G_top = np.diag(np.ones(n) * (-1))
        h_left = np.zeros(n)
        G_bot = np.eye(n)
        h_right = np.ones(n) * C
        G = matrix(np.vstack([G_top, G_bot]), (2 * n, n), 'd')
        h = matrix(np.hstack([h_left, h_right]), (2 * n, 1), 'd')
        P = matrix(np.dot(np.diag(y), np.dot(K, np.diag(y))), (n, n), 'd')
        q = matrix(np.ones(n) * (-1), (n, 1), 'd')

        A = matrix(y, (1, n), "d")

        b = matrix(0.0)
        alpha = y * np.array(solvers.qp(P, q, G, h, A=A, b=b)["x"]).reshape(-1)

        support_vectors = np.where(np.abs(alpha) > self.param.tol)[0]
        intercept = 0
        for sv in support_vectors:
            intercept += y[sv]
            intercept -= np.sum(
                alpha[support_vectors] * K[sv, support_vectors])
        if len(support_vectors) > 0:
            intercept /= len(support_vectors)

        # set to zero non support vectors
        alpha[np.where(np.abs(alpha) <= self.param.tol)[0]] = 0
        
        self._b = intercept
        self._alpha = alpha
        return self._alpha, self._b


if __name__ == "__main__":
    #   from src.tools.test import EasyTest
    dparams = {"small": False, "nsmall": 200}
    kparams = {'g': 8, 'l': 6}
    from src.kernels.gappy import GappyKernel
    from src.data.seq import AllSeqData
    alldata = AllSeqData(parameters=dparams)
    data0 = alldata[0]['train']
    train, val = data0.split(split_val=0.1)

    kernel = GappyKernel(train, parameters=kparams)
    ksvm = KSVM(kernel, parameters={'C': 2})
    ksvm.fit()
    print(ksvm.score_recall_precision(val))
#    EasyTest(kernels="wildcard", data="seq", methods="ksvm", show = False,
#             dparams=dparams, kparams= kparams)

#     from src.kernels.wildcard_trie import WildcardTrieKernel
#     kernel = WildcardTrieKernel(data)
