from call_tx import callTx
from new_account import newAccount


if __name__ == "__main__":

    json_list = []
    with open("json_list.dat","r") as fj:
        lines = fj.readlines()
        for line in lines:
            json_list.append(line.strip("\n"))
    password_list = []
    with open("password_list.dat","r") as fp:
        lines = fp.readlines()
        for line in lines:
            password_list.append(line.strip("\n"))

        
    res = callTx(json_list,password_list,rem)
    f2.write(str(res["result"]))
    if res["status"] == 1:
        json_list, password_list = newAccount(json_list,password_list,res["addrno"],int(2e17))

        with open("json_list.dat","w") as fj:
            for json in json_list:
                fj.write(json+"\n")

        with open("password_list.dat","w") as fp:
            for password in password_list:
                fp.write(password+"\n")
