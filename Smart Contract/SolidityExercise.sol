// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

//create a contract that can store data and return the data back

// be able to do the following;

// 1. receive information 2. store information 3. return the information back

// A contract in the sense of Solidity is a collection of code (its function) and data (its state) that resides at a specific address on the Ethereum blockchain

contract SolidityExercise {
    //write all code inside here - functions and its store
    uint storeData = '10';
    string names = 'junhyun';
    bool switchOn = true;

    //다른 계약에서도 이 함수를 호출할 수 있도록 함
    function set(uint x) public {
        storeData = x;
    }

    //어떤 값을 반환하는지 명시
    function get() public view returns (uint){ //view 가 있어야 경고창이 뜨지 않음 // 함수에 가시성을 부여하면서 상태가 수정되지 않도록 함
        return storeData;
    }

}
