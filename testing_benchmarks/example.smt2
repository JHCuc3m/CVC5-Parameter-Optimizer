(set-logic QF_LIA)
(declare-fun x () Int)
(declare-fun y () Int)
(assert (= (+ x y) 10))
(assert (>= x 0))
(assert (>= y 0))
(check-sat)
(get-model)