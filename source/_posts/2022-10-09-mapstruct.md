---
id: mapstruct
title: "MapStruct - Java bean 映射，简单的方法！"
description: "应用程序通常需要在不同的对象模型（例如实体和 DTO）之间进行映射，如：在前后台传输过程中，持久层定义的实体类经常需要映射到其它的对象模型进行相互转换。"
date: 2022.10.09 18:26
categories:
    - Java
tags: [Java, MapStruct]
keywords: Java Bean, DTO, DO, VO, mapping, MapStruct
cover: /contents/covers/mapstruct.png
---

应用程序通常需要在不同的对象模型（例如实体和 DTO）之间进行映射，如：在前后台传输过程中，持久层定义的实体类经常需要映射到其它的对象模型进行相互转换。

![](/contents/covers/mapstruct.png)

## MapStruct

MapStruct 是一个代码生成器，在不同的对象模型（例如 实体 和 DTO）之间进行映射，它基于约定优于配置的方法，极大地简化了 Java bean 类型之间的映射实现。

MapStruct 是一个 Java 注释处理器，用于生成类型安全、高性能和无依赖关系的 bean 映射代码。

与其他映射框架相比，MapStruct 在编译时生成 bean 映射，这确保了高性能，允许开发人员快速的反馈和彻底的错误检查。

## 引用

- [Maven](https://mapstruct.org/documentation/stable/reference/html/#_apache_maven) - pom.xml

```xml
<properties>
    <org.mapstruct.version>1.5.2.Final</org.mapstruct.version>
</properties>
...
<dependencies>
    <dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct</artifactId>
        <version>${org.mapstruct.version}</version>
    </dependency>
</dependencies>
...
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
                <annotationProcessorPaths>
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>${org.mapstruct.version}</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

- [Gradle](https://mapstruct.org/documentation/stable/reference/html/#_gradle) - build.gradle

```groovy
plugins {
    ...
    id "com.diffplug.eclipse.apt" version "3.26.0" // Only for Eclipse
}

dependencies {
    ...
    implementation "org.mapstruct:mapstruct:${mapstructVersion}"
    annotationProcessor "org.mapstruct:mapstruct-processor:${mapstructVersion}"

    // If you are using mapstruct in test code
    testAnnotationProcessor "org.mapstruct:mapstruct-processor:${mapstructVersion}"
}
```

## 冰山一角 - 基本映射

从基本开始，假设我们有一个代表汽车的类 `Car`（例如一个JPA 实体）和一个数据传输对象 `CarDto`（DTO）。 示例一：

```java
public class Car {
    private String make;
    private int numberOfSeats;
    private CarType type;
    private int price;
    ......
}
```

```java
public class CarDto {
    private String manufacturer;
    private int seatCount;
    private String type;
    private String price;
    ......
}
```

定义映射器的接口，只需在定义的接口上使用注解：`org.mapstruct.Mapper`，示例二：

```java
@Mapper
public interface CarMapper {
    CarMapper INSTANCE = Mappers.getMapper( CarMapper.class );

    @Mapping(target = "manufacturer", source = "make")
    @Mapping(target = "seatCount", source = "numberOfSeats")
    CarDto carToCarDto(Car car);

    @Mapping(target = "fullName", source = "name")
    PersonDto personToPersonDto(Person person);
}
```

在生成的方法实现中，源类型（例如 Car）中的所有可读属性都将被复制到目标类型（例如 CarDto）中的相应属性中：
- 当一个属性与其对应的目标实体同名时，它将被隐式映射。
- 当一个属性在目标实体中具有不同的名称时，可以通过 @Mapping 注解指定其名称

一个接口中可以有多个映射方法，所有这些方法的实现都将由 MapStruct 生成。映射接口的实现可以从 Mappers 类中检出。为便于使用，在接口中声明了一个 INSTANCE 成员实例，供调用者直接访问接口实例。示例三：

```java
// CarMapperTest.java
@Test
public void shouldMapCarToDto() {
    //given
    Car car = new Car( "Morris", 5, CarType.SEDAN );
 
    //when
    CarDto carDto = CarMapper.INSTANCE.carToCarDto( car );
 
    //then
    assertThat( carDto ).isNotNull();
    assertThat( carDto.getMake() ).isEqualTo( "Morris" );
    assertThat( carDto.getSeatCount() ).isEqualTo( 5 );
    assertThat( carDto.getType() ).isEqualTo( "SEDAN" );
}
```

@Mapper 注解使 MapStruct 代码生成器在编译时生成 CarMapper 接口的实现（在 target 目录下对应的路径下）。示例四：

```java
// GENERATED CODE
public class CarMapperImpl implements CarMapper {

    @Override
    public CarDto carToCarDto(Car car) {
        if ( car == null ) {
            return null;
        }

        CarDto carDto = new CarDto();

        if ( car.getFeatures() != null ) {
            carDto.setFeatures( new ArrayList<String>( car.getFeatures() ) );
        }
        carDto.setManufacturer( car.getMake() );
        carDto.setSeatCount( car.getNumberOfSeats() );
        carDto.setDriver( personToPersonDto( car.getDriver() ) );
        carDto.setPrice( String.valueOf( car.getPrice() ) );
        if ( car.getCategory() != null ) {
            carDto.setCategory( car.getCategory().toString() );
        }
        carDto.setEngine( engineToEngineDto( car.getEngine() ) );

        return carDto;
    }

    @Override
    public PersonDto personToPersonDto(Person person) {
        //...
    }
}
```

编译后的代码，看起来像自己写的代码，特别是，这意味着将值从源复制到目标是通过普通的 getter/setter 调用，而不是反射或类似方法。

MapStruct 在许多情况下会自动处理类型转换。生成的代码考虑了通过 @Mapping 指定的任何名称映射。

## 隐式类型转换

源对象和目标对象类型不同的隐式类型转换，目前自动应用以下转换：

- 在所有 Java 原始数据类型和它们对应的包装器类型之间，例如：int，Integer、boolean 等 Boolean。生成的代码是有 null 意识的，即当将包装器类型转换为相应的原始类型时，将执行 null 检查。
- 在所有 Java 原始数字类型和包装类型之间，例如：int 和 long 或 byte 和 Integer。
- 在所有 Java 原始类型（包括它们的包装器）和 String 之间，例如：在 int 和 String 或 Boolean 和 String。还可以指定能够被 java.text.DecimalFormat 解析的格式化字符串。
- 在 Enum 类型 和 String 之间。
- 在大数字类型（java.math.BigInteger, java.math.BigDecimal）和 Java 原始类型（包括它们的包装器）以及字符串之间。还可以指定能够被 java.text.DecimalFormat 解析的格式化字符串。
- 在 java.util.Date/XMLGregorianCalendar 和 String 之间。可以通过 `dateFormat` 选项指定 java.text.SimpleDateFormat 支持的格式化字符串。

> 更多规则，可见 [官方文档](https://mapstruct.org/documentation/stable/reference/html/#implicit-type-conversions)。

示例五：从 int 到 String 的转换

```java
@Mapper
public interface CarMapper {

    @Mapping(source = "price", numberFormat = "$#.00")
    CarDto carToCarDto(Car car);

    @IterableMapping(numberFormat = "$#.00")
    List<String> prices(List<Integer> prices);
}
```

示例六：从 BigDecimal 到 String 的转换

```java
@Mapper
public interface CarMapper {

    @Mapping(source = "power", numberFormat = "#.##E0")
    CarDto carToCarDto(Car car);

}
```

示例七：从 Date 到 String 的转换

```java
@Mapper
public interface CarMapper {

    @Mapping(source = "manufacturingDate", dateFormat = "dd.MM.yyyy")
    CarDto carToCarDto(Car car);

    @IterableMapping(dateFormat = "dd.MM.yyyy")
    List<String> stringListToDateList(List<Date> dates);
}
```

## 映射对象引用

源对象 包含 引用对象 与 目标对象 的转换，也就是 [映射对象引用](https://mapstruct.org/documentation/stable/reference/html/#mapping-object-references) 。

通常，一个对象不仅具有原始类型属性，还可能引用其他对象。例如，Car 类可以包含一个对 Person 对象的引用（代表汽车的驾驶员），这个对象应该被 CarDto 类引用，映射为 PersonDto 对象。

在这种情况下，只需为引用的对象类型定义一个映射方法，示例八：

```java
@Mapper
public interface CarMapper {

    CarDto carToCarDto(Car car);

    PersonDto personToPersonDto(Person person);
}
```

carToCarDto() 方法生成的代码将调用 personToPersonDto() 用于映射驾驶员属性的方法，生成的personToPersonDto() 实现代码负责完成人员对象的映射。

MapStruct 将为源对象和目标对象中的每个属性对按如下步骤生成映射方法的实现：

1. 如果源和目标属性具有相同的类型，则该值将**直接**从源复制到目标。如果该属性是一个集合（例如 List），则该集合的副本将被设置到目标属性中。
1. 如果源属性类型和目标属性类型不同，请检查是否存在**其他映射方法**，其参数类型为源属性类型，返回类型为目标属性类型。如果存在这样的方法，它将在生成的映射实现中调用。
1. 如果不存在这样的方法，MapStruct 将查看属性的源和目标类型的**内置转换是否存在**。如果是这种情况，生成的映射代码将应用此转换。
1. 如果不存在这样的方法，MapStruct 将应用**复杂**的转换：
    a. 映射方法，再对结果使用映射方法，像这样：`target = method1( method2( source ) )`
    b. 内置转换，再对结果使用映射方法，如：`target = method( conversion( source ) )`
    c. 映射方法，再对结果使用内置转换，如：`target = conversion( method( source ) )`
1. 如果没有找到这样的方法，MapStruct 将尝试生成一个自动子映射方法，该方法将在源属性和目标属性之间进行映射。
1. 如果 MapStruct 无法创建基于名称的映射方法，则会在编译时报出错误，指示不可映射的属性及其路径。

## 映射集合

源对象 和 目标对象 同为 集合类型 进行转换，也就是 [映射集合](https://mapstruct.org/documentation/stable/reference/html/#mapping-collections)。

集合类型（List、Set 等）的映射与映射 bean 类型的方式相同，即通过在映射器接口中定义具有所需源和目标类型的映射方法。

MapStruct 支持 Java 集合框架中的各种可迭代类型。示例九：

```java
@Mapper
public interface CarMapper {

    Set<String> integerSetToStringSet(Set<Integer> integers);

    List<CarDto> carsToCarDtos(List<Car> cars);

    CarDto carToCarDto(Car car);
}
```

生成的 `integerSetToStringSet` 代码实现对每个元素从 Integer 到 String 执行转换，而生成的 `carsToCarDtos` 方法调用 `carToCarDto` 方法转换每个元素。如示例十所示：

```java
//GENERATED CODE
@Override
public Set<String> integerSetToStringSet(Set<Integer> integers) {
    if ( integers == null ) {
        return null;
    }

    Set<String> set = new LinkedHashSet<String>();

    for ( Integer integer : integers ) {
        set.add( String.valueOf( integer ) );
    }

    return set;
}

@Override
public List<CarDto> carsToCarDtos(List<Car> cars) {
    if ( cars == null ) {
        return null;
    }

    List<CarDto> list = new ArrayList<CarDto>();

    for ( Car car : cars ) {
        list.add( carToCarDto( car ) );
    }

    return list;
}
```

## 映射枚举类型

源枚举类型中的每个常量都映射到目标枚举类型中同名的常量，即 [映射枚举类型](https://mapstruct.org/documentation/stable/reference/html/#_mapping_enum_to_enum_types)。

如果需要，可以在 `@ValueMapping` 注解的帮助下，将源枚举类中的常量映射到具有另一个名称的常量。还可以将源枚举类中的几个常量映射到目标类型中的同一个常量。示例十一：

```java
@Mapper
public interface OrderMapper {

    OrderMapper INSTANCE = Mappers.getMapper( OrderMapper.class );

    @ValueMappings({
        @ValueMapping(target = "SPECIAL", source = "EXTRA"),
        @ValueMapping(target = "DEFAULT", source = "STANDARD"),
        @ValueMapping(target = "DEFAULT", source = "NORMAL")
    })
    ExternalOrderType orderTypeToExternalOrderType(OrderType orderType);
}
```

生成的代码。示例十二：

```java
// GENERATED CODE
public class OrderMapperImpl implements OrderMapper {

    @Override
    public ExternalOrderType orderTypeToExternalOrderType(OrderType orderType) {
        if ( orderType == null ) {
            return null;
        }

        ExternalOrderType externalOrderType_;

        switch ( orderType ) {
            case EXTRA: externalOrderType_ = ExternalOrderType.SPECIAL;
            break;
            case STANDARD: externalOrderType_ = ExternalOrderType.DEFAULT;
            break;
            case NORMAL: externalOrderType_ = ExternalOrderType.DEFAULT;
            break;
            case RETAIL: externalOrderType_ = ExternalOrderType.RETAIL;
            break;
            case B2B: externalOrderType_ = ExternalOrderType.B2B;
            break;
            default: throw new IllegalArgumentException( "Unexpected enum constant: " + orderType );
        }

        return externalOrderType_;
    }

}
```

## 多个源参数的映射

[多个源参数的映射](https://mapstruct.org/documentation/stable/reference/html/#mappings-with-several-source-parameters)，例如：将几个实体组合成一个数据传输对象。示例十三：

````java
@Mapper
public interface AddressMapper {

    @Mapping(target = "description", source = "person.description")
    @Mapping(target = "houseNumber", source = "address.houseNo")
    DeliveryAddressDto personAndAddressToDeliveryAddressDto(Person person, Address address);
}
````

所示的映射方法将两个不同源对象的属性映射到一个目标对象。与单参数映射方法一样，属性按名称映射。

如果多个源对象中有相同名称的属性，则必须使用注解指定从哪个源中读取属性，否则将会抛出异常。对于在给定源对象中唯一的属性，`source` 属性可以选择性的指定，因为其可以自动确定。

## 条件映射

[条件映射](https://mapstruct.org/documentation/stable/reference/html/#conditional-mapping)：条件映射属于一种 [源存在性检测](https://mapstruct.org/documentation/stable/reference/html/#source-presence-check)，不同于默认的调用 `XYZ` 属性的 `hasXYZ` 方法进行存在性检测，条件映射允许自定义检测方法，来决定是否对属性进行映射。

在方法上使用 `org.mapstruct.Condition` 注解并返回 `boolean` 类型值的方法，即为自定义的条件检测方法。

例如，您只想映射不为 `null` 且不是空的字符串属性时：

````java
@Mapper
public interface CarMapper {

    CarDto carToCarDto(Car car);

    @Condition
    default boolean isNotEmpty(String value) {
        return value != null && !value.isEmpty();
    }
}
````

## 最后

Mapstruct 提供了大量的功能和配置，使我们能够以安全优雅、简单快捷的方式创建从简单到复杂的映射器，减少转换代码。

本文中所介绍到的只是基础常见用法，还有很多强大的功能文中没有提到，想要探索更多、更详细的使用方式可以参考 [官方文档](https://mapstruct.org/documentation/stable/reference/html/)。