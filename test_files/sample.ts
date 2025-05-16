// Sample TypeScript file for testing
class Person {
  private name: string;
  private age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }

  public getInfo(): string {
    return `${this.name} is ${this.age} years old.`;
  }
}

interface Vehicle {
  make: string;
  model: string;
  year: number;
  drive(): void;
}

class Car implements Vehicle {
  make: string;
  model: string;
  year: number;
  
  constructor(make: string, model: string, year: number) {
    this.make = make;
    this.model = model;
    this.year = year;
  }
  
  drive(): void {
    console.log(`Driving a ${this.year} ${this.make} ${this.model}`);
  }
}

// Create instances
const john = new Person("John Doe", 30);
const myCar = new Car("Toyota", "Corolla", 2022);

// Use them
console.log(john.getInfo());
myCar.drive();
