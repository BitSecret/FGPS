## G、代数关系
expr可以是表达式，也可以是实体属性，并且可以嵌套表示。  

    Equal(expr1,expr2)

例：  
Equal(a,5)  
Equal(MeasureOfAngle(ABC),30)  
Equal(Add(LengthOfLine(AB),a+5,x),y^2)  

## H、代数运算
|名称|格式|表达式符号|运算符优先级|
|:--:|:--:|:--:|:--:|
|加|Add(expr1,expr2,…)|+| 1 |
|减|Sub(expr1,expr2)|-| 1 |
|乘|Mul(expr1,expr2,…)|*| 2 |
|除|Div(expr1,expr2)|/| 2 |
|幂|Pow(expr1,expr2)|^| 3 |
|根号|Sqrt(expr1)|√| 4 |
|正弦|Sin(expr)|@| 4 |
|余弦|Cos(expr)|#| 4 |
|正切|Tan(expr)|$| 4 |
|实数|R|1,2,3,...| / |
|自由变量|x|a,b,c,...| / |
|左括号| / |{| 5 |
|右括号| / |}| 0 |  

在使用表达式，若无法判断运算符的优先级，可以使用中括号来强制优先级。  
前5个运算符是双目运算符，如a+5,b-c,x^2；在接下来4个运算符是单目运算符，如√2,@30,#60。

## I、解题目标
### Value(expr)
expr可以是表达式，也可以是实体属性，并且可以嵌套表示。  
代数型解题目标，求某个表达式或属性的值。  

    example: Value(LengthOfLine(AB))
             Value(Add(MeasureOfAngle(ABC),MeasureOfAngle(DEF)))
             Value(x+y)

### Equal(expr1,expr2)
expr可以是表达式，也可以是实体属性，并且可以嵌套表示。 
代数型解题目标，证明左右俩个部分相等。   

    example: Equal(LengthOfLine(AB),x+y)
             Equal(Add(MeasureOfAngle(ABC),MeasureOfAngle(DEF)),Pow(x,2))

### Relation(*)
逻辑型解题目标，求某个实体或属性。  
Relation表示任意实体、实体关系。  

    example: Relation(Parallel(AB,CD))
             Relation(RightTriangle(ABC))    

