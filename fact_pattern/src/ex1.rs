pub trait Animal {
    fn make_sound( &self) ->String;
}

struct Cat;
impl Animal for Cat {
    fn make_sound( &self) ->String {
        "meow".into()
    }
}


struct Dog;
impl Animal for Dog {
    fn make_sound( &self) ->String {
        "Bark Bark".into()
    }
}

// create Factories
pub trait Factory {
    type Animal;

    fn create_animal( &self) ->Self::Animal;
}

struct CatFactory;
impl CatFactory {
    fn new( )-> Self {
        CatFactory
    }
}

impl Factory for CatFactory {
    type Animal = Cat;
    fn create_animal( &self) ->Self::Animal {
        Cat {}
    }
}

struct DogFactory;
impl  DogFactory {
    fn new( )-> Self{
        DogFactory
    }
}

impl  Factory for DogFactory {
    type Animal = Dog;
    fn create_animal( &self) ->Self::Animal {
        Dog {}
    }    
}

fn main() {
    println!( "{}", DogFactory::new().create_animal().make_sound() );
    println!( "{}", CatFactory::new().create_animal().make_sound() );
}
