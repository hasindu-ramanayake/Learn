#[warn(unused_assignments)]

fn main() {
    // let a = 13;
    // let b: f64 = 2.3;
    // let c: f32 = 120.0;

    // let avg = (a as f64 + b + c as f64) / 3.0;

    // assert_eq!( avg ,45.1);
    // println!("Pass the test");


    //arr for rust, multi dim
    // let arrayi32: [[i32; 10]; 10];
    // arrayi32 = [[1;10];10]; 
    // let arr = [[1;2];3];
    // println!("{}", arr[1][1]);
    

    // let cel = 23.0;
    // assert_eq!( cel_fah(cel), 73.4);
    // println!("You pass the challage..!!");

    loopchallage();

}


// fn cel_fah( cel: f64 ) ->f64 {
//     (1.8 * cel) + 32 as f64
// } 

fn loopchallage( )-> () {
    let arr = [1, 9, -2, 0, 23, 20, -7, 13, 37, 20, 56, -18, 20, 3];
    let mut max: i32 = arr[0];
    let mut min: i32 = arr[0];
    let mut sum: f64 = 0.0;

    for &num in arr.iter(){
        if  max < num {
            max = num;
        }

        if min > num {
            min = num;
        }

        sum += num as f64;

    }
    
    sum = sum as f64 / arr.len() as f64;

    assert_eq!(max,56 );
    assert_eq!(min, -18 );
    assert_eq!(sum, 12.5 );

    println!("you pass the challage");

} 