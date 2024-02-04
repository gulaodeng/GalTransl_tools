import os,json,shutil,glob,argparse

INPUT_DIR = "input"
OUTPUT_DIR = "output"
GT_INPUT_DIR = "gt_input"
GT_OUTPUT_DIR = "gt_output"

class GT_SMT:
    def __init__(self,project_dir) -> None:
        self.project_dir = os.path.abspath(project_dir)
        self.input_path = os.path.join(project_dir,INPUT_DIR)
        self.output_path = os.path.join(project_dir,OUTPUT_DIR)
        self.gt_input_path = os.path.join(project_dir,GT_INPUT_DIR)
        self.gt_output_path = os.path.join(project_dir,GT_OUTPUT_DIR)
    def merge(self):
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        for file_name in os.listdir(self.input_path):
            print(f"开始合并文件{file_name}")
            #等待合并的文件列表
            merge_file_list = glob.glob(f"{self.gt_output_path}/{file_name}_SMT*")
            #如果文件不长，没有被分割
            if len(merge_file_list) == 0:
                try:
                    shutil.copy(os.path.join(self.gt_output_path,file_name))
                except:
                    print(f"文件{file_name}不成功.")
                continue
            merge_maxrow = len(merge_file_list)
            merge_row = 1
            merge_data =[]
            #合并
            for merge_file in merge_file_list:
                with open(merge_file,"r",encoding="utf-8") as f:
                    file_data = json.load(f)
                if merge_row == 1:
                    #选择前995个元素，后5个给下个文件
                    merge_data = file_data[0:995]
                elif merge_row == merge_maxrow:
                    #最后一个文件
                    merge_data.extend(file_data[5:])
                else:
                    #中间的文件，取6-995
                    merge_data.extend(file_data[5:995])
                merge_row +=1
            with open(os.path.join(self.output_path, file_name), "w", encoding="utf-8") as f:
                    json.dump(merge_data, f, ensure_ascii=False, indent=4)
            print(f"{file_name}合并完成.")

    def split(self):
        for file_name in os.listdir(self.input_path):
            print(f"开始分割:{file_name}")
            file_path = os.path.join(self.input_path,file_name)
            with open(file_path,"r",encoding="utf-8") as f:
                file_data = json.load(f)
            if(len(file_data) <= 1000 ):
                #文件不长，直接输出
                print(f"{file_name}较短,直接输出.")
                shutil.copy(file_path,self.gt_input_path)
                continue
            file_data_lists = [file_data[i:i+1001] for i in range(0, len(file_data), 990)]
            file_num = 1
            for new_file in file_data_lists:
                new_file_name = f"{file_name}_SMT{str(file_num).zfill(3)}.json"
                with open(os.path.join(self.gt_input_path , new_file_name),"w",encoding="utf-8") as f:
                    json.dump(new_file, f,ensure_ascii=False, indent=2)
                file_num +=1
            print(f"{file_name}分割完成.")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--dir",
    "-d",
    help="项目文件夹",
    default=".",
)
parser.add_argument(
    "--mode",
    "-m",
    choices=["s","split","m","merge"],
    help="模式,split分割文件。merge合并文件",
    required=True,
)
args = parser.parse_args()
if args.mode == ("s" or "split"):
    GT_SMT(args.dir).split()
    print("分割全部完成")
elif args.mode == ("m" or"merge"):
    GT_SMT(args.dir).merge()
    print("合并全部完成")