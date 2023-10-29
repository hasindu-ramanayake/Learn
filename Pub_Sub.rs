//Sub->observer
trait Sub {
    fn updata( &self) -> ();
}

struct Subscriber{
    id: u32,
}

impl PartialEq for Subscriber {
    fn eq( &self, other: &Self ) ->bool {
        self.id == other.id
    }
}

impl Sub for Subscriber {
    fn updata( &self )->() {
        println!("I got the latest notification, {}", self.id );
    }
}

//--------------------------------------------
trait Pub {
    fn subscribe( &mut self, subscriber: Subscriber );
    fn unsubscribe( &mut self, subscriber: Subscriber );
    fn notify( &self);
}

struct Publisher {
    title: String,
    sub_list: Vec< Subscriber >
}

impl Publisher {
    fn new ( title: String ) -> Self {
        Self{ 
            title: title,
            sub_list: Vec::new(),
        }
    }

}

impl Pub for Publisher {
    fn subscribe( &mut self, subscriber: Subscriber ) {
        self.sub_list.push( subscriber);
    }

    fn unsubscribe( &mut self, subscriber: Subscriber ) {
        if let Some(idx) = self.sub_list.iter().position( |x| *x == subscriber) {
            self.sub_list.remove(idx);
        }
    }
    fn notify( &self) {
        for sub in self.sub_list.iter() {
            sub.updata();
        }
    }
}


fn main() {
    let sub_1 = Subscriber { id:1 };
    let sub_2 = Subscriber { id:2 };

    let mut pub_1 = Publisher::new( String::from("HHR") );
    pub_1.subscribe(sub_1);
    pub_1.subscribe(sub_2);
    pub_1.notify();

    let sub_1 = Subscriber { id:1 };
    pub_1.unsubscribe(sub_1);
    pub_1.notify()


}
