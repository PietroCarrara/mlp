(let x 8)
(let y 8)

(defun dec (n)
  (= x (- x n)))

(defun display ()
  (print x)
  (print y))

(defun inc (n)
  (= y (+ y n)))

(defun primeiro ()
  (dec 2)
  (inc 2))

(defun segundo ()
  (let x 3)
  (let y 3)
  (dec 2)
  (display))

(defun main()
  (let y 5)
  (dec 1)
  (inc 1)
  (primeiro)
  (segundo)
  (display))

(main)