
import { useState } from 'react'

export default function Square({turn, setTurn, value, rI, cI, setValue, FindWinner }) {
  const [disable, setDisable] = useState(false)

  function onPress(){
    if (disable) return;
    if (FindWinner()) return;
    setTurn(turn + 1)
    setDisable(true)
    if (turn % 2 == 0 ){
      setValue( (preValue) => {
        const newValue = preValue.map((row, i) => {
          return row.map((cell, j) =>{
            if (i === rI && j === cI) {
              return "X";
            } else {
              return cell;
            }
          } )
        } )
        return newValue;
      })
    } else {
      setValue( (preValue) => {
        const newValue = preValue.map((row, i) => {
          return row.map((cell, j)=>{
            if (i === rI && j === cI) {
              return "O";
            } else {
              return cell;
            }
          })
        })
        return newValue;
      })
    }
    
  }

  return (
    <>
      <button onClick={onPress} className='max-w-full h-52 border rounded-md text-7xl border-red-800'>{value}</button>
    </>
  )
}