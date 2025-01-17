﻿# HW11: Algorithms by Oleg Yaropolov
## Problem 1: two sum
Runtime: **64 ms**, faster than  **70.32%**  of  Python3  online submissions for  Two Sum.
Memory Usage: **15.3 MB**, less than  **55.74%**  of  Python3  online submissions for  Two Sum.

Реализуем алгоритм из лекции. Создадим словарь, в который будем добавлять найденные элементы и их индексы во входящем массиве. Тогда на очередной итерации i:
- Если для текущего элемента массива $\text{nums}[i]$ среди уже добавленных в словарь (просмотренных раннее) элементов есть такой X, что $$\text{nums}[i]+X=\text{target}$$ то найденная пара это то, что мы ищем.  
- Иначе будем добавлять в словарь пару {item: index}  

## Problem 2: 3sum
Runtime: **708 ms**, faster than  **91.49%**  of  Python3  online submissions for  3Sum.
Memory Usage: **17 MB**, less than  **93.97%**  of  Python3  online submissions for  3Sum.

### Алгоритм
Реализуем принцип **two pointers** с лекции. Для этого предварительно отсортируем массив. Так как в отличии от предыдущей задачи нам надо выдать все тройки, удовлетворяющие условиям (а не любую), то создадим set, в который будем записывать найденные тройки. 

Итерируемся по массиву. На шаге i будем искать тройки $\text{nums}[i], \text{nums}[l], \text{nums}[r]$, такие, что $i<l<r$. В начале шага левый указатель на $i+1$, правый - на последнем элементе массива. До тех пор, пока указатели не сойдутся, будем сравнивать сумму $\text{nums}[i] + \text{nums}[l] + \text{nums}[r]$ с нулем. 
- Если сумма меньше нуля, то двигаем левый указатель на +1, увеличивая сумму. 
- Если сумма больше нуля, двигаем правый указатель на -1, уменьшая сумму. 
- Если сумма равна нулю, то мы нашли нужную тройку! Запоминаем ее и идем дальше, сдвигая левый указатель вправо, а правый влево (могут найтись еще тройки на этом проходе). Заметим, что тройка упорядоченная, поэтому можно запоминать как есть. 
Очевидно, что при таком переборе мы ничего не пропустим. 
### Некоторые (но не все) нюансы:
- В развилке If выше сумму стоит считать один раз, запоминать и потом несколько раз сравнивать. Я поначалу считал каждый раз.
- Лучше использовать конструкцию if..elif..else, чтобы исключить лишние проверки (у нас взаимоисключающие условия)
- В начале каждой большой итерации имеет смысл сравнить текущее $\text{nums}[i]$ с нулем. Если оно больше, то все последующие тройки будут давать в сумме больше нуля и можно не искать дальше. 
- Если мы уже проверили число $\text{nums}[i]$ и на следующей итерации попадается оно же - можно пропустить, новых троек мы не найдем. 

## Problem 3: 4sum
Runtime: **652 ms**, faster than  **73.19%**  of  Python3  online submissions for  4Sum.
Memory Usage: **14 MB**, less than  **97.91%**  of  Python3  online submissions for  4Sum.

Сведем задачу к предыдущей. Снова отсортируем массив. Будем итерироваться по всем элементам: $\text{first} \in [0, n-3)$. Для каждого first будем итерироваться по $\text{second} \in [\text{first}, n-2)$. И уже имея зафиксированную пару $\text{first}, \text{second}$ будем среди всех последующих элементов искать с помощью two pointers пару таких, что $$\text{nums}[\text{first}] + \text{nums}[\text{second}] + \text{nums}[l] + \text{nums}[r] = target$$

Для ускорения применим те же идеи, что и в предыдущей задаче. Я применил их внутри первого итерирования, но можно и внутри второго. Общая идея всех этих ускорений - мы ускоряемся в каких-то кейсах за счет замедления в других. Соответственно, нужно отталкиваться от целевой среды при использовании тех или иных ускорений.  
