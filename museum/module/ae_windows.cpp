#include <vector>
#include <string>
#include <fstream>

#define API __declspec(dllexport) // Windows-specific export

unsigned int getFileSize(std::string filePath){
	std::ifstream is(filePath, std::ifstream::binary);
	if (is) {
		is.seekg(0, is.end);
		int length = (int)is.tellg();
		is.seekg(0, is.beg);
		return length;
	}
	return -1;
}

unsigned int ReadFile(std::string filePath, unsigned char **_data, unsigned int *remainLength)
{
	unsigned int maxReadSize = (unsigned int) 1024*1024*1024*2;
	std::ifstream is(filePath, std::ifstream::binary);
	if (is) {
		// seekg를 이용한 파일 크기 추출
		is.seekg(0, is.end);
		unsigned int totalLength = (unsigned int)is.tellg();
		unsigned int curStartPoint = totalLength - *remainLength;
		is.seekg(curStartPoint, is.beg);

		if(*remainLength >= maxReadSize){
			unsigned char * buffer = (unsigned char*)malloc(maxReadSize-1);
			is.read((char*)buffer, maxReadSize-1);
			is.close();
			*_data = buffer;
			*remainLength = *remainLength-maxReadSize-1;
			return maxReadSize-1;
		} else {
			unsigned int targetReadSize = *remainLength;
			unsigned char * buffer = (unsigned char*)malloc(targetReadSize);
			is.read((char*)buffer, targetReadSize);
			is.close();
			*_data = buffer;
			*remainLength = 0;
			return targetReadSize;
		}
	}
	return -1;
}

extern "C" API unsigned int ae_chunking_from_path(const char* filePath, unsigned int** anchorArrPointer, const unsigned int windowSize) {
	std::vector<unsigned int> anchorVec;
    unsigned char* buffer;
	unsigned int remainLength = getFileSize(filePath);
	while(remainLength){
		unsigned int readLength = ReadFile(std::string(filePath), &buffer, &remainLength);
		unsigned int cursorIdx = 0;
		unsigned int lastCursorIdx = 0;
		int maxValue, maxIdx;
		while (cursorIdx < readLength) {
			maxValue = (unsigned char)buffer[cursorIdx];
			maxIdx = cursorIdx;
			cursorIdx++;
			while (cursorIdx < readLength) {
				if ((unsigned char)buffer[cursorIdx] <= maxValue) {
					if (cursorIdx == maxIdx + windowSize) {
						anchorVec.push_back(cursorIdx);
						lastCursorIdx = cursorIdx;
						cursorIdx++;
						break;
					}
				}
				else {
					maxValue = (unsigned char)buffer[cursorIdx];
					maxIdx = cursorIdx;
				}
				cursorIdx++;
			}
		}
		if (lastCursorIdx != cursorIdx) {
			anchorVec.push_back(cursorIdx);
		}
		free(buffer);
	}
	unsigned int *tempAnchorArr = (unsigned int*)malloc(sizeof(unsigned int) * anchorVec.size());
	for (auto it = anchorVec.begin(); it != anchorVec.end(); it++) {
		tempAnchorArr[std::distance(anchorVec.begin(), it)] = *it;
	}
	*anchorArrPointer = tempAnchorArr;
	return anchorVec.size();
}


extern "C" API unsigned int ae_chunking_from_bytes(const unsigned char* buffer, unsigned int length, unsigned int** anchorArrPointer, const unsigned int windowSize) {
	std::vector<unsigned int> anchorVec;
	unsigned int cursorIdx = 0;
	unsigned int lastCursorIdx = 0;
	int maxValue, maxIdx;
	while (cursorIdx < length) {
		maxValue = (unsigned char)buffer[cursorIdx];
		maxIdx = cursorIdx;
		cursorIdx++;
		while (cursorIdx < length) {
			if ((unsigned char)buffer[cursorIdx] <= maxValue) {
				if (cursorIdx == maxIdx + windowSize) {
					anchorVec.push_back(cursorIdx);
					lastCursorIdx = cursorIdx;
					cursorIdx++;
					break;
				}
			}
			else {
				maxValue = (unsigned char)buffer[cursorIdx];
				maxIdx = cursorIdx;
			}
			cursorIdx++;
		}
	}
	if (lastCursorIdx != cursorIdx) {
		anchorVec.push_back(cursorIdx);
	}
	unsigned int* anchorArr = (unsigned int*)malloc(sizeof(unsigned int) * anchorVec.size());
	for (auto it = anchorVec.begin(); it != anchorVec.end(); it++) {
		anchorArr[std::distance(anchorVec.begin(), it)] = *it;
	}
	*anchorArrPointer = anchorArr;
	return anchorVec.size();
}

extern "C" API void release(unsigned int* anchorArrPointer) {
	free(anchorArrPointer);
}