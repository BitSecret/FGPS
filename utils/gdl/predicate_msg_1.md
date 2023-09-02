# 附录2 谓词标注对照手册
## A、基本构图谓词
基本构图谓词有三个，分别是Shape(图形)、Collinear(点共线)和Cocircular(点共圆)。推理器可以根据这三个构图谓词自动扩展出基本谓词，其扩展树如下图所示：  
<div align=center>
    <img src="cowork-pic/auto-expand.png" width="50%">
</div>

### Shape(*)
Shape是最基本的构图谓词，它使用若干个边或弧来声明一个几何图形，这个几何图形可以是一条边，可以是一个角，也可以是边和弧围成的图形。使用Shape声明几何图形时，我们需要依据有序原则、逆时针原则和旋转不变原则，这三大原则的介绍可参考cowork.md。  
<div>
    <img src="gdl-pic/P001.png" width="60%">
</div>

**1.声明一个点**  
如图1所示，P是圆O的圆心，我们可以这样声明一个点：  

    Shape(P)

**2.声明一条线段**  
如图2所示，AB是线段的两点，我们可以这样声明线段：  

    Shape(AB)

当使用Shape声明线段时，默认线段是无向的，所以这样声明也是合法的：

    Shape(BA)

**3.声明一个角**  
如图3所示，角B由两条线段构成。需要注意，在声明角时，线段是有向的，两条线出现的顺序按照逆时针的方向，首尾相接。因此角B可以表示为：  

    Shape(AB,BC)

**4.声明一个封闭图形**  
如果一个边一个边或一个角一个角来声明图形，未免也太麻烦了。我们可以直接声明一个由若干线段和弧构成的图形，在构图阶段，推理器会自动扩展出图形中的角、线和弧。因此我们在标注图形的构图语句时，先使用Shape声明所有的最小封闭图形，然后在把那些不封闭的最小图形如角、线段、点等声明，就可以声明整个图形。  
对于图3中的四边形，我们可以这样声明：  

    Shape(AB,BC,CD,DA)
    Shape(BC,CD,DA,AB)
    Shape(CD,DA,AB,BC)
    Shape(DA,AB,BC,CD)

根据旋转不变原则，一个四边形有上述四种表示，我们选择一种就可以。  
更复杂的图形，如图4，可以声明为：  

    Shape(OAB,BE,EA)
    Shape(OBC,CE,EB)
    Shape(EC,OCD,DP,PE)
    Shape(AE,EP,PD,ODA)

需注意，虽然EP和PD是共线的，但在声明封闭图形时，不能直接声明ED，需要把最小的边都声明出来。  
封闭图形可以由线和弧构成，线有两个方向，弧只有一个方向。在声明线时，需要按照逆时针的方向，各点首尾相接；声明弧时，需注意弧只有一种表示方法。  
当弧单独出现时，不需要使用Shape来声明，因为弧的出现必然伴随着Cocircular谓词，所有弧将会由Cocircular谓词自动扩展得到。  

### Collinear(*)
Collinear用来声明3个及3个以上的共线点，2点一定是共线的，所以不用声明2点。  
<div>
    <img src="gdl-pic/P002.png" width="45%">
</div>

共线声明是及其简单的，只要按顺序列出一条线上所有的点即可，如图1中的共线可声明为：  

    Collinear(AMB)

共线没有方向之分，从另一个方向声明也是合法的：  

    Collinear(BMA)

图2中的共线可声明为：  

    Collinear(BCDEF)

图3中的共线可声明为：  

    Collinear(ADB)
    Collinear(AEC)

共线会在推理器中自动扩展出所有的线和平角，如Collinear(AMB)会扩展得到Line(AM),Line(MB),Line(AM),Angle(AMB),Angle(BMA)。  

### Cocircular(O,*)
Cocircular用来声明共圆的若干个点，与Collinear相同，按照顺序列出若干点即可；但也与Collinear不同，一是即使1个点在圆上也要声明，二是共圆的声明按照逆时针方向，且从任何点开始都可。  
<div>
    <img src="gdl-pic/P003.png" width="60%">
</div>

在图1中，共圆的几点可声明为：  

    Cocircular(O,ABCD)
    Cocircular(O,BCDA)
    Cocircular(O,CDAB)
    Cocircular(O,DABC)

依据三大原则，图1的共圆声明可以有上述4种形式，任选其1即可。图2到图4是几种比较特殊的共圆声明。
图2的圆上只有1个点，也要声明：  

    Cocircular(O,A)

图3圆上没有点，也要声明：  

    Cocircular(O)

图4两圆有公共点，要分别声明：  

    Cocircular(O,AB)
    Cocircular(P,BA)

共圆声明后，会自动扩展出所有的弧和圆。  

## B、基本实体
基本实体是由基本构图扩展来的实体，在构图结束后不会再改变。我们无需声明基本实体，下述内容是为了让我们理解形式化系统的内在逻辑。基本构图谓词声明一个图形的结构信息，也就是点的相对位置信息。基本实体相当于是基本构图的 'unzip' 版本，在推理过程中更方便使用。目前推理器内置了10个基本实体。  

### Point(A)
就是点，没什么好说的。  
<div>
    <img src="gdl-pic/P004.png"  width="45%">
</div>

图1-3的点的声明：  

    Point(A)
    Point(A),Point(B),Point(C)
    Point(A),Point(C),Point(O)

### Line(AB)
Line声明一个无向线段。
<div>
    <img src="gdl-pic/P005.png"  width="45%">
</div>

因为是无向的，所以图1的线段有两种声明方法，选其一即可：  

    Line(AB)
    Line(BA)

图2和图3的线段声明：  

    Line(AB),Line(CD)  
    Line(AO),Line(BO) 


### Arc(OAB)
Arc声明一段弧，由3个点组成，第1个点是弧所在的圆，其余2点是构成弧的点，按照逆时针的方向有序列出。  
<div>
    <img src="gdl-pic/P006.png"  width="45%">
</div>

图1-3中弧的声明：  

    Arc(OAB)
    Arc(OAC),Arc(OCA)
    Arc(OAB),Arc(OBC),Arc(OCD),Arc(ODA)

### Angle(ABC)
角由3个点构成，在声明角时，需要按照逆时针原则。  
<div>
    <img src="gdl-pic/P007.png"  width="45%">
</div>

图1-3的角的声明：  

    Angle(AOB)
    Angle(ABC),Angle(BCA),Angle(CAB)
    Angle(AOC),Angle(COB),Angle(BOD),Angle(DOA)

### Polygon(*)
多边形由若干个直线构成，按照逆时针的方向列出所有的点。依据旋转不变原则，一个n边形有n种表示方式。  
<div>
    <img src="gdl-pic/P008.png"  width="45%">
</div>

    Polygon(ABC),Polygon(BCA),Polygon(CAB)
    Polygon(ABCD),Polygon(BCDA),Polygon(CDAB),Polygon(DABC)
    Polygon(ABCDE),Polygon(BCDEA),Polygon(CDEAB),Polygon(DEABC),Polygon(EABCD)

### Circle(O)
Circle用于声明一个圆，O表示圆心。  
<div>
    <img src="gdl-pic/P009.png"  width="45%">
</div>

图1-3中圆的声明： 

    Cirlce(O)
    Cirlce(B),Cirlce(A)
    Cirlce(O)


