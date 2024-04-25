// SPDX-License-Identifier: SPDX-License
pragma solidity ^0.8.4;

contract Will {
    address owner;
    uint fortune;
    bool deceased;

    constructor() payable {
        owner = msg.sender; // msg sender represents address being called
        fortune = msg.value; //msg value tells us how much ether is being sent
        deceased = false;
    }

    // 계약을 호출할 수 있는 사람은 owner뿐
    modifier onlyOwner {
        require(msg.sender == owner);
        _; //함수가 계속되게함 제어자를 확인하고 실행하던 함수로 돌아감
        //조건에 안맞으면 여기서 막힘
    }

    // 할아버지가 돌아가셨을 때만 자금 분배

    modifier mustBeDeceased {
        require(deceased == true);
        _;
    }

    // list of family wallets
    address payable[] familyWallets;

    // map through inheritance
    mapping(address => uint) inheritance; //key-store value

    //
    function setInheritance(address payable wallet, uint amount) public onlyOwner{
        //to add wallets to the family wallet
        familyWallets.push(wallet);
        inheritance[wallet] = amount;
    }

    // set inheritance for each address
    function payout() private mustBeDeceased { //우리만 접근
        for(uint i=0; i < familyWallets.length; i++) {
            familyWallets[i].transfer(inheritance[familyWallets[i]]);
            // transferring funds from contract address to reciever address
        }
    }

    // oracle switch
    function hasDeceased() public onlyOwner {
        deceased = true;
        payout();
    }

}